# Define any utility functions for Elo rating calculations or other purposes

import math
import pandas as pd
import json
import numpy as np
import os
import trueskill
from PIL import Image
import pprint
from datetime import datetime


def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_a - rating_b) / 400))


def update_rating(rating, expected_score, actual_score, k_factor=32):
    return rating + k_factor * (actual_score - expected_score)


def add_player(name, default_img=False):
    players = load_players()
    if default_img:
        img_path = f"default.png"
    else:
        img_path = f"{len(players)}.png"
    new_row = {"name": name, "img_path": img_path, 'guest': True}
    new_player = pd.DataFrame([new_row])
    players = pd.concat([players, new_player], ignore_index=True)
    save_players(players)
    return img_path


def load_players():
    return pd.read_csv('static/players.csv')


def save_players(players):
    players.to_csv('static/players.csv', index=False)


def load_games():
    with open('static/games.json', 'r') as json_file:
        games = json.load(json_file)
    return games


def save_games(games):
    pprint.pprint(games, width=120, compact=True)
    pretty_json_str = pprint.pformat(games, width=120, compact=True, sort_dicts=False).replace("'", '"')

    with open('static/games.json', 'w') as f:
        f.write(pretty_json_str)


def load_ratings():
    return np.genfromtxt('static/tmp/ratings.csv', delimiter=',')


def save_ratings(ratings):
    if not os.path.exists('static/tmp'):
        os.makedirs('static/tmp')
    np.savetxt('static/tmp/ratings.csv', ratings, delimiter=',')


def load_ratings_history():
    with open('static/tmp/ratings_history.json', 'r') as json_file:
        ratings_history = json.load(json_file)
    return ratings_history


def save_ratings_history(ratings_history):
    if not os.path.exists('static/tmp'):
        os.makedirs('static/tmp')
    with open('static/tmp/ratings_history.json', 'w') as json_file:
        json.dump(ratings_history, json_file)


def save_csv(data, file_name):
    np.savetxt(os.path.join('static', 'tmp', file_name), data, delimiter=',')


def load_csv(file_name):
    return np.genfromtxt(os.path.join('static', 'tmp', file_name), delimiter=',')


def register_game(player_ids, result):
    assert len(player_ids) == len(result)
    games = load_games()

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    games.append({"time": formatted_time, "player_ids": player_ids, "result": result})
    save_games(games)
    calculate_ratings()


def calculate_ratings():
    players = load_players()
    trueskill_env = trueskill.TrueSkill(draw_probability=0.0, tau=25/3/100)
    ratings = [trueskill_env.create_rating() for _ in range(len(players))]
    games = load_games()

    # for game in games:
    #     player_ids = game["player_ids"]
    #     result = game["result"]
    #
    #     new_ratings = trueskill.rate([[ratings[id]] for id in player_ids], ranks=result)
    #
    #     for i, player_id in enumerate(player_ids):
    #         ratings[player_id] = new_ratings[i][0]
    #
    #     for player_id in player_ids:
    #         ratings_history[player_id].append((ratings[player_id].mu - 3 * ratings[player_id].sigma) * 40)

    ratings_history = [[0] for _ in range(len(players))]
    net_point_gains = np.zeros(shape=(len(players), len(players)))
    games_won = np.zeros(shape=(len(players), len(players)), dtype=int)
    games_played = np.zeros(shape=(len(players), len(players)), dtype=int)

    for game in games:
        player_ids = game["player_ids"]
        result = game["result"]

        new_ratings = [[ratings[id].mu, ratings[id].sigma] for id in player_ids]
        for player_a in range(len(player_ids) - 1):
            for player_b in range(player_a + 1, len(player_ids)):
                player_a_id, player_b_id = player_ids[player_a], player_ids[player_b]
                rating_a, rating_b = ratings[player_a_id], ratings[player_b_id]
                if result[player_a] < result[player_b]:
                    tmp_ratings = trueskill.rate_1vs1(rating_a, rating_b, env=trueskill_env)
                else:
                    tmp_ratings = trueskill.rate_1vs1(rating_b, rating_a, env=trueskill_env)[::-1]

                new_ratings[player_a][0] += (tmp_ratings[0].mu - rating_a.mu) / (len(player_ids)-1)
                new_ratings[player_a][1] += (tmp_ratings[0].sigma - rating_a.sigma) / (len(player_ids)-1)
                new_ratings[player_b][0] += (tmp_ratings[1].mu - rating_b.mu) / (len(player_ids)-1)
                new_ratings[player_b][1] += (tmp_ratings[1].sigma - rating_b.sigma) / (len(player_ids)-1)

                net_point_gains[player_a_id, player_b_id] += (tmp_ratings[0].mu - rating_a.mu) / (len(player_ids)-1)
                net_point_gains[player_b_id, player_a_id] += (tmp_ratings[1].mu - rating_b.mu) / (len(player_ids)-1)

                won = int(result[player_a] < result[player_b])
                games_won[player_a_id, player_b_id] += won
                games_won[player_b_id, player_a_id] += 1-won
                games_played[player_a_id, player_b_id] += 1
                games_played[player_b_id, player_a_id] += 1

        for i, player_id in enumerate(player_ids):
            ratings[player_id] = trueskill_env.create_rating(mu=new_ratings[i][0], sigma=new_ratings[i][1])

        for player_id in player_ids:
            ratings_history[player_id].append((ratings[player_id].mu - 3 * ratings[player_id].sigma) * 40)

    save_ratings([x[-1] for x in ratings_history])
    save_ratings_history(ratings_history)
    save_csv(net_point_gains, 'net_point_gains.csv')
    save_csv(games_won, 'games_won.csv')
    save_csv(games_played, 'games_played.csv')

    players_mu_sigma = np.array([[rating.mu*40, rating.sigma*40] for rating in ratings])
    save_csv(players_mu_sigma, 'players_mu_sigma.csv')


# def calculate_ratings():
#     players = load_players()
#     ratings = [1000 for _ in range(len(players))]
#     ratings_history = [[1000] for _ in range(len(players))]
#     games = load_games()
#
#     for game in games:
#         player_ids = game["player_ids"]
#         result = game["result"]
#         n_players = len(player_ids)
#         for i in range(n_players-1):
#             for j in range(i+1, n_players):
#                 if result[i] == result[j]:
#                     actual_score = 0.5
#                 elif result[i] > result[j]:
#                     actual_score = 1
#                 else:
#                     actual_score = 0
#
#                 player_id_i, player_id_j = player_ids[i], player_ids[j]
#                 rating_i, rating_j = ratings[player_id_i], ratings[player_id_j]
#                 exp_score = calculate_expected_score(rating_i, rating_j)
#                 ratings[player_id_i] = update_rating(rating_i, 1-exp_score, 1-actual_score)
#                 ratings[player_id_j] = update_rating(rating_j, exp_score, actual_score)
#         for player_id in player_ids:
#             ratings_history[player_id].append(ratings[player_id])
#
#     save_ratings(ratings)
#     save_ratings_history(ratings_history)


def load_players_dict():
    players = load_players()
    ratings = load_ratings()
    players = players.to_dict(orient='records')
    for id, (player, rating) in enumerate(zip(players, ratings)):
        player['id'] = id
        player['rounded_rating'] = round(rating)
    return players


def load_players_ordered_list():
    players = load_players_dict()
    ratings = load_ratings()
    players_all = [players[i] for i in np.argsort(ratings)[::-1]]
    return players_all


def crop_to_square(img):
    width, height = img.size

    min_dimension = min(width, height)

    left = (width - min_dimension) // 2
    top = (height - min_dimension) // 2
    right = (width + min_dimension) // 2
    bottom = (height + min_dimension) // 2

    # Crop the image
    img_cropped = img.crop((left, top, right, bottom))
    return img_cropped.resize((512, 512), Image.ANTIALIAS)



