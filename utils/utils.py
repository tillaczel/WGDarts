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
