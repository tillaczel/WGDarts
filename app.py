from flask import Flask, request, redirect, url_for, render_template
import os
import csv
from PIL import Image
from werkzeug.utils import secure_filename

# Configure your application and upload folder
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to store player data
players = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Load the players from the CSV file for the index page as well
    player_data = load_players()
    return render_template('index.html', players=player_data)

@app.route('/add_player', methods=['POST'])
def add_player():
    # Add player logic including image upload handling
    player_name = request.form['name']
    player_elo = request.form['elo_rating']  # Assuming you have a field for the Elo rating in your form
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Open the image and resize it if necessary
            with Image.open(file_path) as img:
                if img.size != (250, 250):
                    img = img.resize((250, 250))
                    img.save(file_path)  # Save the resized image

            # Update the players dictionary and optionally save to CSV
            players[player_name] = {'elo_rating': player_elo, 'image': url_for('static', filename=f'uploads/{filename}')}
            # Here you should also add the logic to save this data to your CSV file
    return redirect(url_for('index'))

@app.route('/remove_player', methods=['POST'])
def remove_player():
    # Remove player logic
    player_name = request.form['name']
    if player_name in players:
        # Remove player from dictionary and optionally update the CSV file
        players.pop(player_name)
    return redirect(url_for('index'))

@app.route('/players')
def show_players():
    # Use the load_players function to load player data for the players page
    player_data = load_players()
    return render_template('players.html', players=player_data)

# Function to load players data from CSV
def load_players():
    loaded_players = []
    with open('players.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            loaded_players.append(row)
    return loaded_players

if __name__ == '__main__':
    app.run(debug=True)

