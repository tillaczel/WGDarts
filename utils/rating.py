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
import copy

from .utils import get_player_rating


def get_ratings(all_ratings, player2games):
    ratings = defaultdict(float)
    for player_id in player2games.keys():
        ratings[player_id] = all_ratings[player2games[player_id][-1]][player_id]
    return ratings


def calculate_game_ratings(ratings, result):
    trueskill_env = trueskill.TrueSkill(draw_probability=0.0, tau=25 / 3 / 100)

    old_ratings = copy.deepcopy(ratings)
    for player_a in range(len(old_ratings) - 1):
        for player_b in range(player_a + 1, len(ratings)):
            rating_a = trueskill_env.create_rating(mu=old_ratings[player_a]['mu'] / 40,
                                                   sigma=old_ratings[player_a]['sigma'] / 40)
            rating_b = trueskill_env.create_rating(mu=old_ratings[player_b]['mu'] / 40,
                                                   sigma=old_ratings[player_b]['sigma'] / 40)
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


def calculate_ratings(games):
    ratings = defaultdict(NewPlayer)

    games_ratings_path = os.path.join('static', 'data', "ratings.jsonl")
    games_ratings_before_path = os.path.join('static', 'data', "ratings_before.jsonl")
    if os.path.exists(games_ratings_path):
        os.remove(games_ratings_path)
    if os.path.exists(games_ratings_before_path):
        os.remove(games_ratings_before_path)

    player2games = defaultdict(list)

    for game_idx, game in enumerate(games):
        player_ids = game["player_ids"]
        result = game["result"]
        game_ratings = [ratings[id] for id in player_ids]

        _game_ratings = {id: r for id, r in zip(player_ids, game_ratings)}
        with jsonlines.open(games_ratings_before_path, 'a') as writer:
            writer.write(_game_ratings)
        game_ratings = calculate_game_ratings(game_ratings, result)
        _game_ratings = {id: r for id, r in zip(player_ids, game_ratings)}
        with jsonlines.open(games_ratings_path, 'a') as writer:
            writer.write(_game_ratings)
        [player2games[p_id].append(game_idx) for p_id in player_ids]



def register_game(ratings, player_ids, result):
    assert len(player_ids) == len(result)

    rating_before = [get_player_rating(ratings, id) for id in player_ids]
    rating = calculate_game_ratings(copy.deepcopy(rating_before), result)

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    game = {"time": formatted_time, "player_ids": player_ids, "result": result}

    rating = {id: r for id, r in zip(player_ids, rating)}
    rating_before = {id: r for id, r in zip(player_ids, rating_before)}

    return game, rating, rating_before
