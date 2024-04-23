import sqlite3
from Spotipy_helper import get_artist_names_by_genre 
import restaurants_helper
import FamousBirthdays_helper


def setup_database():
    conn = sqlite3.connect('spotify_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            genre_id INTEGER,
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        )
    ''')
    conn.commit()
    conn.close()
    

if __name__ == '__main__':
    setup_database()
    genres = ['hip-hop', 'party', 'k-pop', 'jazz', 'classical']
    
