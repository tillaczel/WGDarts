# Define any utility functions for Elo rating calculations or other purposes

import copy
import json
import jsonlines
import math
import numpy as np
import os
import pandas as pd
import pprint
import trueskill
from PIL import Image
from collections import defaultdict
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


def get_ratings(all_ratings, player2games):
    ratings = defaultdict(float)
    for player_id in player2games.keys():
        ratings[player_id] = all_ratings[player2games[player_id][-1]][player_id]
    return ratings


def register_game(player_ids, result):
    assert len(player_ids) == len(result)
    games = load_games()

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    games.append({"time": formatted_time, "player_ids": player_ids, "result": result})
    save_games(games)
    calculate_ratings()


def calculate_game_ratings(ratings, result):
    trueskill_env = trueskill.TrueSkill(draw_probability=0.0, tau=25 / 3 / 100)

    new_ratings = copy.deepcopy(ratings)
    for player_a in range(len(new_ratings) - 1):
        for player_b in range(player_a + 1, len(ratings)):
            rating_a = trueskill_env.create_rating(mu=new_ratings[player_a]['mu'] / 40,
                                                   sigma=new_ratings[player_a]['sigma'] / 40)
            rating_b = trueskill_env.create_rating(mu=new_ratings[player_b]['mu'] / 40,
                                                   sigma=new_ratings[player_b]['sigma'] / 40)
            if result[player_a] < result[player_b]:
                tmp_ratings = trueskill.rate_1vs1(rating_a, rating_b, env=trueskill_env)
            else:
                tmp_ratings = trueskill.rate_1vs1(rating_b, rating_a, env=trueskill_env)[::-1]

            ratings[player_a]['mu'] += (tmp_ratings[0].mu - rating_a.mu) / (len(ratings) - 1) * 40
            ratings[player_a]['sigma'] += (tmp_ratings[0].sigma - rating_a.sigma) / (len(ratings) - 1) * 40
            ratings[player_b]['mu'] += (tmp_ratings[1].mu - rating_b.mu) / (len(ratings) - 1) * 40
            ratings[player_b]['sigma'] += (tmp_ratings[1].sigma - rating_b.sigma) / (len(ratings) - 1) * 40

    return ratings


class NewPlayer(dict):
    def __init__(self, mu=1000., sigma=1000 / 3, **kwargs):
        super().__init__(**kwargs)
        self['mu'] = mu
        self['sigma'] = sigma


def calculate_ratings():
    games = load_games()
    ratings = defaultdict(NewPlayer)

    if not os.path.exists('static'):
        os.makedirs('static')
    games_ratings_path = os.path.join("static", "ratings.jsonl")
    games_ratings_before_path = os.path.join("static", "ratings_before.jsonl")
    if os.path.exists(games_ratings_path):
        os.remove(games_ratings_path)
    if os.path.exists(games_ratings_before_path):
        os.remove(games_ratings_before_path)

    player2games = defaultdict(list)

    for game_idx, game in enumerate(games):
        player_ids = game["player_ids"]
        result = game["result"]
        game_ratings = [ratings[id] for id in player_ids]

        with jsonlines.open(games_ratings_before_path, 'a') as writer:
            writer.write(game_ratings)
        game_ratings = calculate_game_ratings(game_ratings, result)
        game_ratings = {id: r for id, r in zip(player_ids, game_ratings)}
        with jsonlines.open(games_ratings_path, 'a') as writer:
            writer.write(game_ratings)
        [player2games[p_id].append(game_idx) for p_id in player_ids]

    with open('static/player2games.json', 'w') as f:
        json.dump(dict(player2games), f)


class WinRatio(dict):
    def __init__(self, played=0, won=0, **kwargs):
        super().__init__(**kwargs)
        self['played'] = played
        self['won'] = won


def games_2_win_ratios(games, main_player_id):
    win_ratio = defaultdict(WinRatio)
    for game in games:
        player_ids = game["player_ids"]
        result = game["result"]
        main_player_idx = player_ids.index(main_player_id)
        main_player_result = result[main_player_idx]
        for p_id, r in zip(player_ids, result):
            if p_id == main_player_id:
                continue
            win_ratio[p_id]['played'] += 1
            if main_player_result < r:
                win_ratio[p_id]['won'] += 1
    return win_ratio


def get_game_history(all_ratings, player2games, main_player_id):
    game_idxs = player2games[main_player_id]
    ratings = {'mu': [1000], 'sigma': [1000 / 3]}
    for game_idx in game_idxs:
        rating = all_ratings[game_idx][main_player_id]
        ratings['mu'].append(rating['mu'])
        ratings['sigma'].append(rating['sigma'])
    return ratings


def load_players_dict():
    players = load_players()
    all_ratings = []
    with jsonlines.open(os.path.join('static', 'ratings.jsonl'), 'r') as reader:
        for line in reader:
            line = {int(k): v for k, v in line.items()}
            all_ratings.append(line)
    with open(os.path.join('static', 'player2games.json'), 'r') as json_file:
        player2games = json.load(json_file)
    player2games = {int(k): v for k, v in player2games.items()}
    final_ratings = get_ratings(all_ratings, player2games)
    players = players.to_dict(orient='records')
    for id, player in enumerate(players):
        ratings_player = get_game_history(all_ratings, player2games, id)
        rating = final_ratings[id]
        player['id'] = id
        player['mu'] = round(rating['mu'])
        player['sigma'] = round(rating['sigma'])
        player['rating'] = rating['mu'] - 3 * rating['sigma']
        player['mus'] = ratings_player['mu']
        player['sigmas'] = ratings_player['sigma']
        player['ratings'] = (np.array(player['mus']) - 3 * np.array(ratings_player['sigma'])).tolist()
        player['rounded_rating'] = round(player['rating'])
    return players


def load_players_ordered_list():
    players = load_players_dict()
    players_all = sorted(players, key=lambda x: -x['rating'])
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
