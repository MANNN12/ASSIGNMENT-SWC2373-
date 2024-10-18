from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
WEBEX_API_BASE = 'https://webexapis.com/v1'

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

def get_headers(access_token):
    """Helper function to set up headers with access token."""
    return {'Authorization': f'Bearer {access_token}'}

def get_user_info(access_token):
    """Fetch user information based on the access token."""
    headers = get_headers(access_token)
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to get user info: {response.status_code} - {response.text}")
        return None

def get_rooms(access_token):
    """Fetch the rooms of the user."""
    headers = get_headers(access_token)
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        logging.error(f"Failed to get rooms: {response.status_code} - {response.text}")
        return None

def get_connection_status(access_token):
    """Check the connection status."""
    headers = get_headers(access_token)
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    if response.status_code == 200:
        return {'status': 'Connection is valid'}
    else:
        logging.error(f"Failed to verify connection: {response.status_code} - {response.text}")
        return {'status': 'Failed to connect, invalid token or connection issue'}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        user_info = get_user_info(access_token)
        if user_info:  # If token is valid, store it in session
            session['access_token'] = access_token
            flash("Login successful!", "success")
            return redirect(url_for('menu'))
        else:
            flash("Invalid access token. Please try again.", "danger")
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/menu', methods=['GET'])
def menu():
    access_token = session.get('access_token')
    if not access_token:
        flash("Access token is required. Please log in.", "warning")
        return redirect(url_for('index'))
    return render_template('menu.html')

@app.route('/user_info', methods=['GET'])
def user_info():
    access_token = session.get('access_token')
    if not access_token:
        flash("Access token is required. Please log in.", "warning")
        return redirect(url_for('index'))
    
    user_info = get_user_info(access_token)
    if user_info:
        return render_template('user_info.html', user_info=user_info)
    else:
        flash("Failed to retrieve user info.", "danger")
        return redirect(url_for('menu'))

@app.route('/rooms', methods=['GET'])
def rooms():
    access_token = session.get('access_token')
    if not access_token:
        flash("Access token is required. Please log in.", "warning")
        return redirect(url_for('index'))

    rooms = get_rooms(access_token)
    if rooms is not None:
        return render_template('rooms.html', rooms=rooms)
    else:
        flash("Failed to retrieve rooms.", "danger")
        return redirect(url_for('menu'))

@app.route('/connection_status', methods=['GET'])
def connection_status():
    access_token = session.get('access_token')
    if not access_token:
        flash("Access token is required. Please log in.", "warning")
        return redirect(url_for('index'))

    status = get_connection_status(access_token)
    if status:
        return render_template('connection_status.html', status=status)
    else:
        flash("Failed to retrieve connection status.", "danger")
        return redirect(url_for('menu'))

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear the session
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)