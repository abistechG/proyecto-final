import os 
from flask import Flask, session, url_for,redirect, request

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__) #initialize the flask app
app.config['SECRET_KEY'] = 'a_static_secret_key'

client_id = '5f83f8e7bebf4896a37737a50d9ef4b5' #found from spotify api 
client_secret = 'c026360848cd451793486a8707591140'#found from spotify api 
redirect_url = 'http://localhost:5000/callback' 
scope = 'playlist-read-private' #must be changed to accomodate project scope dummy for now. Use comma to use more than one scope




cache_handler = FlaskSessionCacheHandler(session) # Storing acccess token of Spotipy in Flask session
sp_ouath = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_url,
    scope= scope,
    cache_handler= cache_handler,
    show_dialog=True
 ) #used for authenitcating with spotify API 

sp = Spotify(auth_manager=sp_ouath)

@app.route('/')
def home():
    if not sp_ouath.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_ouath.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))

@app.route('/callback')
def callback():
    sp_ouath.get_access_token(request.args['code'])  # Properly exchange the code for a token
    return redirect(url_for('get_playlists'))
     
@app.route('/get_playlists')
def get_playlists():
    if not sp_ouath.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_ouath.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    playlist_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join([f'{name} : {url}' for name, url in playlist_info])
    return playlists_html
#code used to run the flask application locally 
if __name__ == '__main__':
    app.run(debug=True)
    
