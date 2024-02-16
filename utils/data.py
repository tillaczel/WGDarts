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


def load_players():
    return pd.read_csv('static/data/players.csv')


def save_players(players):
    players.to_csv('data/players.csv', index=False)


def load_games():
    with open('static/data/games.json', 'r') as json_file:
        games = json.load(json_file)
    return games


def save_games(games):
    pprint.pprint(games, width=120, compact=True)
    pretty_json_str = pprint.pformat(games, width=120, compact=True, sort_dicts=False).replace("'", '"')

    with open('static/data/games.json', 'w') as f:
        f.write(pretty_json_str)
