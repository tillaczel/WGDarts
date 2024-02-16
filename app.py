import json
import numpy as np
import os
import random
import time
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import utils

# Configure your application and upload folder
app = Flask(__name__)
IMAGE_FOLDER = 'static/data/uploads'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER


@app.route('/')
def index():
    players_df = utils.load_players()
    games = utils.load_data('games.jsonl')
    ratings = utils.load_data('ratings.jsonl', key2int=True)

    players = utils.process_players_dict(players_df, games, ratings)
    players_list = utils.order_players(players)
    timestamp = int(time.time())
    return render_template('index.html', players=players_list, timestamp=timestamp)


@app.route('/start_game', methods=['POST'])
def start_game():
    players_df = utils.load_players()
    games = utils.load_data('games.jsonl')
    ratings = utils.load_data('ratings.jsonl', key2int=True)

    players = utils.process_players_dict(players_df, games, ratings)
    selected_player_ids = [int(i) for i in request.form.getlist('selected_players')]

    players_list = utils.order_players(players)
    selected_players = [player for player in players_list if player['id'] in selected_player_ids]
    random.shuffle(selected_players)

    return render_template('game.html', players=selected_players)


@app.route('/record_results', methods=['POST'])
def record_results():
    games = utils.load_data('games.jsonl')
    ratings = utils.load_data('ratings.jsonl', key2int=True)

    positions = [int(p[:-2]) for p in request.form.getlist('finishPosition')]
    player_ids = [int(id) for id in request.form.getlist('playerId')]
    game, rating, rating_before = utils.rating.register_game(ratings, player_ids, positions)

    game_idx = len(games)
    utils.append_data(game, 'games.jsonl'), games.append(game)
    utils.append_data(rating, 'ratings.jsonl'), ratings.append(rating)
    utils.append_data(rating_before, 'ratings_before.jsonl'), ratings.append(rating_before)
    return redirect(url_for('index'))


@app.route('/player_statistics/<int:player_id>')
def player_statistics(player_id):
    players_df = utils.load_players()
    games = utils.load_data('games.jsonl')
    ratings = utils.load_data('ratings.jsonl', key2int=True)

    players = utils.process_players_dict(players_df, games, ratings)
    player = players[player_id]

    win_ratio = utils.games_2_win_ratios(player['games'], player_id)
    sorted_keys = sorted(win_ratio, key=lambda k: -win_ratio[k]['played'])
    win_ratio_print = []
    for player_id in sorted_keys:
        games_played, games_won = win_ratio[player_id]['played'], win_ratio[player_id]['won']
        ratio = games_won / games_played
        win_ratio_print.append([players[player_id]["name"], int(games_played), f"{ratio:.2%}"])
    player['win_ratio_print'] = win_ratio_print

    total_played, total_won = int(np.sum([v['played'] for v in win_ratio.values()])), int(
        np.sum([v['won'] for v in win_ratio.values()]))
    player['num_challengers'] = total_played
    player['total_win_rate'] = f"{total_won / total_played:.2%}"
    return render_template('player_statistics.html', player_id=player_id, player=player)


@app.route('/admin')
def admin_page():
    players_df = utils.load_players()
    games = utils.load_data('games.jsonl')
    ratings = utils.load_data('ratings.jsonl', key2int=True)

    players = utils.process_players_dict(players_df, games, ratings)
    players = sorted(players, key=lambda d: d['name'])
    return render_template('admin.html', player_list=players)


@app.route('/add_player', methods=['POST'])
def add_player():
    players_df = utils.load_players()

    player_name = request.form['name']
    file = request.files['image']
    players_df, image_path = utils.add_player(players_df, player_name, default_img=len(file.filename) == 0)
    if len(file.filename) != 0:
        img = Image.open(file.stream)
        img = utils.crop_to_square(img)
        img.save(os.path.join(app.config['IMAGE_FOLDER'], image_path))
    utils.save_players(players_df)
    return redirect(url_for('index'))


@app.route('/reupload_photo', methods=['POST'])
def reupload_photo():
    players_df = utils.load_players()

    selected_player_id = request.form['player_id']
    file = request.files['image']

    image_path = f"{selected_player_id}.png"
    img = Image.open(file.stream)
    img = utils.crop_to_square(img)
    img.save(os.path.join(app.config['IMAGE_FOLDER'], image_path))

    players_df['img_path'].iloc[int(selected_player_id)] = image_path
    utils.save_players(players_df)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
