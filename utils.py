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
    ratings = [trueskill.Rating() for _ in range(len(players))]
    ratings_history = [[0] for _ in range(len(players))]
    games = load_games()

    for game in games:
        player_ids = game["player_ids"]
        result = game["result"]

        new_ratings = trueskill.rate([[ratings[id]] for id in player_ids], ranks=result)

        for i, player_id in enumerate(player_ids):
            ratings[player_id] = new_ratings[i][0]

        for player_id in player_ids:
            # ratings_history[player_id].append((ratings[player_id].mu) * 40)
            ratings_history[player_id].append((ratings[player_id].mu - 3 * ratings[player_id].sigma) * 40)

    save_ratings([x[-1] for x in ratings_history])
    save_ratings_history(ratings_history)


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



