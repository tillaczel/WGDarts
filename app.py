from flask import Flask, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import utils
import numpy as np
import random

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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
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
    # Access form data
    result = {}
    players = utils.load_players_dict()
    for player in players:
        finish_order_key = f"finish_order_{player['id']}"
        finish_order_value = request.form.get(finish_order_key)
        if finish_order_value is not None:
            result[player['id']] = int(finish_order_value)
    utils.register_game(list(result.keys()), list(result.values()))

    # After processing, redirect back to the index
    return redirect(url_for('index'))


@app.route('/player_statistics/<int:player_id>')
def player_statistics(player_id):
    # Add your logic to fetch and display player statistics here
    players = utils.load_players_dict()
    ratings_history = utils.load_ratings_history()
    return render_template('player_statistics.html', player_id=player_id, player=players[player_id], ratings_history=ratings_history[player_id])


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)

