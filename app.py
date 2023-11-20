
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
    # ...

@app.route('/remove_player', methods=['POST'])
def remove_player():
    # Remove player logic
    # ...

# Add other routes as necessary

if __name__ == '__main__':
    app.run(debug=True)
