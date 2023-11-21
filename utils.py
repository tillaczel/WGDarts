# Define any utility functions for Elo rating calculations or other purposes

import math
import pandas as pd


def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_rating(rating, expected_score, actual_score, k_factor=32):
    return rating + k_factor * (actual_score - expected_score)


def add_player(name, img_path):
    players = load_players()
    new_row = {"name": name, "img_path": img_path, "elo": 1000}
    players = players.append(new_row, ignore_index=True)
    save_players(players)


def load_players():
    return pd.read_csv('static/players.csv')


def save_players(players):
    players.to_csv('static/players.csv', index=False)



def register_game(player_ids, result):
    assert len(player_ids) == len(result)
    n_players = len(player_ids)
    for i in range(n_players-1):
        for j in range(i+1, n_players):
            pass

