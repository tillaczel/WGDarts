from flask import Flask, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import utils
import numpy as np
import random
from PIL import Image

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
    return render_template('index.html', players=players_list)

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
    players_mu_sigma = utils.load_csv('players_mu_sigma.csv')
    games_won = utils.load_csv('games_won.csv')
    games_played = utils.load_csv('games_played.csv')

    player['num_challengers'] = int(np.sum(games_played[player_id]))
    player['win_rate'] = f"{np.sum(games_won[player_id])/player['num_challengers']:.2%}"
    player['mu'] = round(players_mu_sigma[player_id][0])
    player['sigma'] = round(players_mu_sigma[player_id][1])
    ratings_history = utils.load_ratings_history()
    return render_template('player_statistics.html', player_id=player_id, player=player, ratings_history=ratings_history[player_id])


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)

