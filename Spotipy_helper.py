import os
from flask import Flask, session, url_for, redirect, request, jsonify, render_template_string
import logging
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

# Directory for saving playlist tracks
playlist_dir = 'playlist_tracks'

# Create directory if it doesn't exist
if not os.path.exists(playlist_dir):
    os.makedirs(playlist_dir)

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

def fetch_diverse_playlists(limit=5):
    valid_playlists = []
    total_checked = 0
    while len(valid_playlists) < limit:
        playlists = sp.featured_playlists(limit=limit - len(valid_playlists), offset=total_checked)['playlists']['items']
        for playlist in playlists:
            tracks = sp.playlist_tracks(playlist['id'])['items']
            artist_count = {}
            for item in tracks:
                for artist in item['track']['artists']:
                    artist_count[artist['name']] = artist_count.get(artist['name'], 0) + 1
            max_songs_by_single_artist = max(artist_count.values(), default=0)
            if max_songs_by_single_artist / len(tracks) <= 0.1:  
                valid_playlists.append(playlist)
            total_checked += 1
    return valid_playlists

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('featured_playlists'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('featured_playlists'))

@app.route('/featured_playlists')
def featured_playlists():
    try:
        playlists = fetch_diverse_playlists(limit=5)
        playlists_display = render_template_string('''
            <h1>Featured Playlists with Diverse Artists</h1>
            <ul>
                {% for playlist in playlists %}
                    <li><a href="{{ url_for('playlist_details', playlist_id=playlist.id) }}">{{ playlist.name }}</a></li>
                {% endfor %}
            </ul>
        ''', playlists=playlists)
        return playlists_display
    except Exception as e:
        logging.error(f"Error fetching featured playlists: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/playlist_details/<playlist_id>')
def playlist_details(playlist_id):
    try:
        playlist = sp.playlist(playlist_id)
        tracks = sp.playlist_tracks(playlist_id)['items']
        # Extract track details and popularity
        track_details = [
            {
                'name': item['track']['name'],
                'artist': item['track']['artists'][0]['name'],
                'popularity': item['track']['popularity']
            }
            for item in tracks if item['track']
        ]

        # Sort tracks by popularity, descending
        sorted_tracks = sorted(track_details, key=lambda x: x['popularity'], reverse=True)

        details_display = render_template_string('''
            <h1>Tracks in Playlist: {{ playlist.name }}</h1>
            <ul>
                {% for track in sorted_tracks %}
                    <li>{{ track.name }} by {{ track.artist }}</li>
                {% endfor %}
            </ul>
            <a href="{{ url_for('featured_playlists') }}">Back to Playlists</a>
        ''', playlist=playlist, sorted_tracks=sorted_tracks)

        # Write playlist details to file, only saving the first artist's name
        file_path = os.path.join(playlist_dir, f"{playlist['name']}.txt")
        with open(file_path, 'w') as file:
            for track in sorted_tracks:
                file.write(f"{track['artist']}\n")

        return details_display
    except Exception as e:
        logging.error(f"Error fetching playlist details: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':

     app.run(host='0.0.0.0', port=5001, debug=True)
