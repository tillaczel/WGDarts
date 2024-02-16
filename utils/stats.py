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

from .utils import get_player_rating


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


def process_players_dict(players, all_ratings, player2games):
    player2games = {int(k): v for k, v in player2games.items()}
    final_ratings = [get_player_rating(all_ratings, player_id) for player_id in range(len(players))]
    players = players.to_dict(orient='records')
    for id, player in enumerate(players):
        id = int(id)
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


def order_players(players):
    players_all = sorted(players, key=lambda x: -x['rating'])
    return players_all
