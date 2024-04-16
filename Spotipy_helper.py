import os 
from flask import Flask,session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__) #initialize the flask app
app.config['SECRET_KEY'] = os.urandom(64) 

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

#code used to run the flask application locally 
if __name__ == '__main__':
    app.run(debug=True)
    
