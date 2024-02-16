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


def add_player(players, name, default_img=False):
    if default_img:
        img_path = f"default.png"
    else:
        img_path = f"{len(players)}.png"
    new_row = {"name": name, "img_path": img_path, 'guest': True}
    new_player = pd.DataFrame([new_row])
    players = pd.concat([players, new_player], ignore_index=True)
    return players, img_path


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


def get_player_rating(ratings, player_id):
    for ratings_i in ratings[::-1]:
        if player_id in ratings_i.keys():
            return ratings_i[player_id]
    return {'mu': 1000, 'sigma': 1000 / 3}


def player2game_idxs(games, player_id):
    game_idxs = []
    for i, game in enumerate(games):
        if player_id in game['player_ids']:
            game_idxs.append(i)
    return game_idxs

