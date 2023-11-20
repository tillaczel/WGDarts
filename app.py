from flask import Flask, request, redirect, url_for, render_template
import os
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
    return render_template('index.html', players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    # Add player logic including image upload handling
    player_name = request.form['name']
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            players[player_name] = {'image': url_for('static', filename=f'uploads/{filename}')}
    return redirect(url_for('index'))

@app.route('/remove_player', methods=['POST'])
def remove_player():
    # Remove player logic
    player_name = request.form['name']
    if player_name in players:
        players.pop(player_name)
    return redirect(url_for('index'))

# Add other routes as necessary

if __name__ == '__main__':
    app.run(debug=True)

