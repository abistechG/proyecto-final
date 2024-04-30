import http.server
import socketserver
import webbrowser
import os
from urllib.parse import urlparse, parse_qs, quote_plus
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Create a directory to store details of playlist tracks.
playlist_dir = 'playlist_tracks'
if not os.path.exists(playlist_dir):
    os.makedirs(playlist_dir)

# Spotify API credentials. These are required for accessing Spotify's Web API.
client_id = '5f83f8e7bebf4896a37737a50d9ef4b5'
client_secret = 'c026360848cd451793486a8707591140'
redirect_uri = 'http://localhost:5001/callback'
scope = 'playlist-read-private,playlist-read-collaborative,user-top-read'

# Setup Spotify OAuth handler to manage user authorization and token acquisition.
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

# Initialize Spotify client with the auth manager.
sp = Spotify(auth_manager=sp_oauth)

def fetch_diverse_playlists(limit=5, offset=0):
    valid_playlists = []
    total_checked = offset
    # Fetch playlists until we meet the required number of valid playlists.
    while len(valid_playlists) < limit:
        playlists = sp.featured_playlists(limit=limit - len(valid_playlists), offset=total_checked)['playlists']['items']
        for playlist in playlists:
            tracks = sp.playlist_tracks(playlist['id'])['items']
            artist_count = {}
            # Count occurrences of each artist in the playlist.
            for item in tracks:
                for artist in item['track']['artists']:
                    artist_count[artist['name']] = artist_count.get(artist['name'], 0) + 1
            max_songs_by_single_artist = max(artist_count.values(), default=0)
            # Validate playlist diversity: no artist should dominate the playlist.
            if max_songs_by_single_artist / len(tracks) <= 0.1:
                valid_playlists.append(playlist)
            total_checked += 1
    return valid_playlists

def display_playlist_details(playlist_id):
    playlist = sp.playlist(playlist_id)
    tracks = sp.playlist_tracks(playlist_id)['items']
    track_details = [{
        'name': item['track']['name'],
        'artist': item['track']['artists'][0]['name'],
        'spotify_id': item['track']['id'],
        'popularity': item['track']['popularity']
    } for item in tracks]
    
    # Sort tracks by popularity before saving.
    sorted_tracks = sorted(track_details, key=lambda x: x['popularity'], reverse=True)
    file_path = os.path.join(playlist_dir, f"{playlist['name']}.txt")
    with open(file_path, 'w') as file:
        for track in sorted_tracks:
            file.write(f"{track['artist']}\n")
    return sorted_tracks

# HTTP server to handle Spotify OAuth callback and display fetched playlists.
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_path = urlparse(self.path)
        if url_path.path == '/callback':
            query = parse_qs(url_path.query)
            code = query.get('code', [None])[0]
            if code:
                # Retrieve the access token using the code from Spotify.
                token_info = sp_oauth.get_access_token(code)
                playlists = fetch_diverse_playlists()
                message = "Playlists Fetched Successfully! Check console/output files for details."
                for playlist in playlists:
                    tracks = display_playlist_details(playlist['id'])
                    print(f"Playlist: {playlist['name']}, Tracks: {len(tracks)}")
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(message.encode())
            else:
                self.send_error(400, "No code found in the URL query.")
        else:
            self.send_error(404, "Path not found.")

def start_server():
    # Start an HTTP server to handle authentication requests.
    with socketserver.TCPServer(("", 5001), RequestHandler) as httpd:
        print("Server started at localhost:5001")
        url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={quote_plus(redirect_uri)}&scope={quote_plus(scope)}&show_dialog=True"
        webbrowser.open(url)
        httpd.handle_request() 

if __name__ == '__main__':
    start_server()

