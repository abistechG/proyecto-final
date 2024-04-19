import os
from flask import Flask, session, url_for, redirect, request, jsonify
import logging
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


artist_dir = 'artist_names'


if not os.path.exists(artist_dir):
    os.makedirs(artist_dir)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_static_secret_key'

# Spotify API credentials
client_id = '5f83f8e7bebf4896a37737a50d9ef4b5'
client_secret = 'c026360848cd451793486a8707591140'
redirect_url = 'http://localhost:5001/callback'
scope = "playlist-read-private,playlist-read-collaborative,user-top-read"


# Setup Spotify OAuth handler
cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_url,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

# Initialize Spotify client
sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    global sp
    sp = Spotify(auth_manager=sp_oauth)
    return redirect(url_for('select_genre'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])  # Properly exchange the code for a token
    return redirect(url_for('select_genre'))

def get_available_genre_seeds():
    try:
        genre_seeds = sp.recommendation_genre_seeds()
        return genre_seeds['genres']  # This returns a list of available genre seeds
    except Exception as e:
        logging.error(f"Failed to fetch genre seeds: {str(e)}")
        return []

# You can use this function somewhere in your code to check or log available genres
print(get_available_genre_seeds())

@app.route('/select_genre')
def select_genre():
    return '''
    <h1>Select a Genre</h1>
    <ul>
        <li><a href="/genre_recommendations/hip-hop">Hip Hop</a></li>
        <li><a href="/genre_recommendations/party">Party</a></li>
        <li><a href="/genre_recommendations/k-pop">Kpop</a></li>
        <li><a href="/genre_recommendations/jazz">Jazz</a></li>
        <li><a href="/genre_recommendations/classical">Classical</a></li>
    </ul>
    '''

@app.route('/genre_recommendations/<genre_name>')
def get_genre_recommendations(genre_name):
    if not sp:
        return "Spotify client not initialized. Please authenticate first.", 403

    try:
        results = sp.recommendations(seed_genres=[genre_name], limit=100)
        tracks_info = [(track['name'], track['artists'][0]['name'], track['popularity']) for track in results['tracks']]
        sorted_tracks = sorted(tracks_info, key=lambda x: x[2], reverse=True)
        top_tracks = sorted_tracks[:5]

        # Extract artist names from the top tracks
        artist_names = [track[1] for track in top_tracks]

        # Define the path for the file based on the genre
        file_path = os.path.join(artist_dir, f"{genre_name}_artists.txt")

        # Write artist names to a text file within the designated folder
        with open(file_path, "w") as file:
            for name in artist_names:
                file.write(name + "\n")

        return jsonify(top_tracks)
    except Exception as e:
        logging.error(f"Failed to fetch recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5001, debug=True)