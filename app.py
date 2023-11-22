from flask import Flask, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import utils
import numpy as np

# Configure your application and upload folder
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to store player data
players = utils.load_players()
utils.calculate_ratings()
ratings = utils.load_ratings()
players = players.to_dict(orient='records')
for id, (player, rating) in enumerate(zip(players, ratings)):
    player['id'] = id
    player['rounded_rating'] = round(rating)
players = [players[i] for i in np.argsort(ratings)[::-1]]
print(players)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    player_name = request.form['name']
    image_path = utils.add_player(player_name)
    file = request.files['image']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
    return redirect(url_for('index'))

@app.route('/remove_player', methods=['POST'])
def remove_player():
    # Remove player logic
    player_name = request.form['name']
    if player_name in players:
        players.pop(player_name)
    return redirect(url_for('index'))


@app.route('/start_game', methods=['POST'])
def start_game():
    selected_player_ids = request.form.getlist('selected_players')
    print(request.form)
    # Filter to only include selected players
    selected_players = {pid: players[pid] for pid in selected_player_ids if pid in players}
    # Calculate probabilities, implement your logic or method here
    # ...
    return render_template('game.html', players=selected_players)

@app.route('/record_results', methods=['POST'])
def record_results():
    # Logic to process game results goes here

    # After processing, redirect back to the index
    return redirect(url_for('index'))


@app.route('/player_statistics/<int:player_id>')
def player_statistics(player_id):
    # Add your logic to fetch and display player statistics here
    return render_template('player_statistics.html', player_id=player_id)

if __name__ == '__main__':
    app.run(debug=True)

