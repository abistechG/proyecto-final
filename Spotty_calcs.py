from Calcs_plots import set_up_database, spotified_tables, add_missing_columns,fetch_and_store_data
import sqlite3

def spotified_tables(cursor,conn):
    # Create tables with modifications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT UNIQUE NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Playlists (
        playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_name TEXT UNIQUE NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Songs (
        song_id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_name TEXT NOT NULL,
        artist_id INTEGER NOT NULL,
        playlist_id INTEGER NOT NULL,
        spotify_track_id TEXT UNIQUE NOT NULL,
        duration_seconds INTEGER NOT NULL,
        popularity INTEGER not NULL,
        FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
        FOREIGN KEY (playlist_id) REFERENCES Playlists(playlist_id)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FetchState (
        state_id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_playlist_offset INTEGER
    )''')

    # Initialize the FetchState table if empty
    cursor.execute("INSERT OR IGNORE INTO FetchState (last_playlist_offset) VALUES (0)")
    conn.commit()




curry, conny = set_up_database('popularity_central.db')
    #Collect data of Spotify featured Playlist 
spotified_tables(curry,conny)
add_missing_columns(curry, conny)
fetch_and_store_data(curry,conny)

curry.close()
    