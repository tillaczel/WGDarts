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
    players.to_csv('static/data/players.csv', index=False)


def load_data(name, key2int=False):
    f_path = os.path.join('static', 'data', name)
    with jsonlines.open(f_path, 'r') as reader:
        if key2int:
            data = [{int(k): v for k, v in line.items()} for line in reader]
        else:
            data = [line for line in reader]
    return data


def append_data(data, name):
    f_path = os.path.join('static', 'data', name)
    with jsonlines.open(f_path, 'a') as writer:
        writer.write(data)

