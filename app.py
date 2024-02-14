from flask import Flask, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import utils
import numpy as np
import random
from PIL import Image
import time
import json

# Configure your application and upload folder
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


utils.calculate_ratings()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    players_list = utils.load_players_ordered_list()
    timestamp = int(time.time())
    return render_template('index.html', players=players_list, timestamp=timestamp)




@app.route('/start_game', methods=['POST'])
def start_game():
    selected_player_ids = request.form.getlist('selected_players')

    players_list = utils.load_players_ordered_list()
    selected_players = [player for player in players_list if str(player['id']) in selected_player_ids]
    random.shuffle(selected_players)

    return render_template('game.html', players=selected_players)

@app.route('/record_results', methods=['POST'])
def record_results():
    print(request.form)
    positions = [int(p[:-2]) for p in request.form.getlist('finishPosition')]
    ids = [int(id) for id in request.form.getlist('playerId')]
    print(ids, positions)
    utils.register_game(ids, positions)
    return redirect(url_for('index'))


@app.route('/player_statistics/<int:player_id>')
def player_statistics(player_id):
    # Add your logic to fetch and display player statistics here
    players = utils.load_players_dict()
    player = players[player_id]
    # players_mu_sigma = utils.load_csv('players_mu_sigma.csv')
    # games_won = utils.load_csv('games_won.csv')
    # games_played = utils.load_csv('games_played.csv')

    with open(os.path.join('static', 'games.json'), 'r') as json_file:
        games = json.load(json_file)
    with open(os.path.join('static', 'player2games.json'), 'r') as json_file:
        player2games = json.load(json_file)
    player_games = [games[index] for index in player2games[str(player_id)]]
    win_ratio = utils.games_2_win_ratios(player_games, player_id)
    sorted_keys = sorted(win_ratio, key=lambda k: -win_ratio[k]['played'])
    win_ratio_print = []
    for player_id in sorted_keys:
        games_played, games_won = win_ratio[player_id]['played'], win_ratio[player_id]['won']
        ratio = games_won/games_played
        win_ratio_print.append([players[player_id]["name"], int(games_played), f"{ratio:.2%}"])

    total_played, total_won = int(np.sum([v['played'] for v in win_ratio.values()])), int(np.sum([v['won'] for v in win_ratio.values()]))
    player['num_challengers'] = total_played
    player['win_rate'] = f"{total_won/total_played:.2%}"
    # ratings_history = utils.load_ratings_history()
    return render_template('player_statistics.html', player_id=player_id, player=player, ratings_history=[], win_rate=win_ratio_print, players=players)


@app.route('/admin')
def admin_page():
    players = utils.load_players_dict()
    players = sorted(players, key=lambda d: d['name'])
    return render_template('admin.html', player_list=players)


@app.route('/add_player', methods=['POST'])
def add_player():
    player_name = request.form['name']
    file = request.files['image']
    if len(file.filename) > 0:
        image_path = utils.add_player(player_name)
        img = Image.open(file.stream)
        img = utils.crop_to_square(img)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
    else:
        utils.add_player(player_name, default_img=True)
    return redirect(url_for('index'))


@app.route('/reupload_photo', methods=['POST'])
def reupload_photo():
    selected_player_id = request.form['player_id']
    # player_name = request.form['name']
    # print(request.form)
    file = request.files['image']

    image_path = f"{selected_player_id}.png"
    img = Image.open(file.stream)
    img = utils.crop_to_square(img)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))

    players = utils.load_players()
    print(players['img_path'].iloc[int(selected_player_id)])
    players['img_path'].iloc[int(selected_player_id)] = image_path
    utils.save_players(players)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

