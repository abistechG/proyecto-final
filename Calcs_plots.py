import sqlite3
import os
from restaurants_helper import cache_location, city_IDs, restaurant_info
from Spotipy_helper import fetch_diverse_playlists, display_playlist_details
import re
import csv
import requests
from FamousBirthdays_helper import calculate_age
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


def append_artist_to_file(artist_name):
    with open("artists.txt", "a") as file:
        file.write(artist_name + "\n")

def add_missing_columns(cursor,conn):
    

    # Check if 'duration_seconds' column exists and add it if it does not
    cursor.execute("PRAGMA table_info(Songs)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'duration_seconds' not in columns:
        try:
            cursor.execute("ALTER TABLE Songs ADD COLUMN duration_seconds INTEGER")
        except sqlite3.OperationalError as e:
            print(f"Error adding duration_seconds: {e}")

    # Check if 'popularity' column exists and add it if it does not
    if 'popularity' not in columns:
        try:
            cursor.execute("ALTER TABLE Songs ADD COLUMN popularity INTEGER")
        except sqlite3.OperationalError as e:
            print(f"Error adding popularity: {e}")

    conn.commit()
    

#Restaurante 
def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn
    
def create_restaurants_table(cur,conn):
    '''
    initializes restaurant table (for restaurants within a city(s)
    '''
    
    #cur.execute("DROP TABLE IF EXISTS restaurants")
    cur.execute(''' CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY,
        name TEXT,
        num_reviews NUMBER,
        num_rating NUMBER,
        city_id INTEGER
        )
                ''')
    
    conn.commit()
    
def create_cities_table(cur,conn):
    '''
    initializes a city data table (for top five artist's city)
    '''
   # cur.execute("DROP TABLE IF EXISTS cities")
    cur.execute('''CREATE TABLE IF NOT EXISTS cities (
        city_id INTEGER PRIMARY KEY,
        name TEXT
    )
                ''')
    conn.commit()

def create_artistInfo(cur,conn):
    '''
    initializes an artist data table from spotify playlists
    '''
    
    cur.execute('''CREATE TABLE IF NOT EXISTS artists(
    artist_id INTEGER,
    age INTEGER,
    city_id INTEGER,
    playlist_id INTEGER
    );

                ''')
    conn.commit()

def add_cities(city_name:str, city_id:int, cur,conn):
    '''
    adds city name (from external input) and city id (from city_IDs)
    onto cities data table 
    '''
    cur.execute('''
                INSERT INTO cities (city_id, name)
                VALUES (?,?)
                ''',
                (city_id, city_name))
    
    conn.commit()

def add_artistInfo(name:str, age:int, city:str, cur,conn):
    '''
    adds city name (from external input) and city id (from city_IDs)
    onto cities data table 
    '''
    artist_id = cur.execute('''SELECT artist_id,
                    FROM Artist
                    WHERE artist_name = ?''',
                    (name))
    
    artist_id = cur.fetchall()
    
    for aID in artist_id:
        a_ID = aID[0]
    
    
    cur.execute('''
                INSERT INTO artists (artist_id)
                VALUES (?)
                ''',
                (a_ID))
    
    playlist_id = cur.execute('''SELECT playlist_id,
                    FROM Songs
                    WHERE artist_name = ?''',
                    (a_ID))
    playlist_id = cur.fetchall()
    
    for pid in playlist_id:
        p_id = pid[0]
    
    cur.execute('''
                INSERT INTO artists (playlist_id)
                VALUES (?)
                ''',
                (p_id))
    
    cur.execute('''
                INSERT INTO artists (age)
                VALUES (?)
                ''',
                (age))
    
    city_id = cur.execute('''SELECT city_id,
                    FROM cities
                    WHERE name = ?''',
                    (city))
    
    city_id = cur.fetchall()
    
    for cidee in city_id:
        c_id = cidee[0]
    
    cur.execute('''
                INSERT INTO artists (city_id)
                VALUES (?)
                ''',
                (c_id))
    
    
    
    conn.commit()


def add_restaurants(restaurants: dict, city_id: int, cur, conn, limit: int = 25):
    '''
    adds restaurant data from dictionary (restaurant_info) and puts 
    on restaurant data table
    returns if we should continue to next city
    '''
    count_path = "insertion_count.txt"
    
    
    if not os.path.exists(count_path):
        with open(count_path, "w") as f:     
            f.write("0")
    
    
    with open(count_path, "r+") as f:
        count = int(f.read().strip() or 0)     #limits data inserted to 25
       
        new_count = count + limit
                                                    
        
        entries_to_add = list(restaurants.items())[count:min(new_count, len(restaurants))]
        
        for name, details in entries_to_add:
            print(name)
            
            if details.get('number of reviews') not in [None, ""]:
                num_reviews = float(details['number of reviews'])
            else:
                num_reviews = 0
                
            if details.get('rating') not in [None, ""]:
                num_rating = float(details['rating'])
            else:
                num_rating = 0
            print(num_reviews)
            print(num_rating)
           
            cur.execute('''
                        INSERT INTO restaurants (name, num_reviews, num_rating, city_id)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (name, num_reviews, num_rating, city_id))
        
        conn.commit()
        f.seek(0)
        f.truncate()
        
        
        if count >= len(restaurants):
            return 'next'
        
        f.write(str(min(new_count, len(restaurants))))
        
    return 'stay'

 #Musica
 # Connect to the SQLite database

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

# Updated function to fetch and store data with offset and duplication check
def fetch_and_store_data(cursor,conn):
    # Retrieve the last offset
    cursor.execute("SELECT last_playlist_offset FROM FetchState")
    offset = cursor.fetchone()[0]
    
    # Fetch playlists starting from the last offset
    playlists = fetch_diverse_playlists(limit=5, offset=offset)
    songs_added = 0
    
    for playlist in playlists:
        if songs_added >= 25:
            break
        tracks = display_playlist_details(playlist['id'])
        for track in tracks:
            if songs_added >= 25:
                break
            # Check if the song has already been added
            cursor.execute("SELECT song_id FROM Songs WHERE spotify_track_id = ?", (track['spotify_id'],))
            if cursor.fetchone() is None:  # Only proceed if the song hasn't been added
                artist_name = track['artist']
                song_name = track['name']
                spotify_track_id = track['spotify_id']
                popularity = track['popularity']
                duration_sec = track['duration_sec']
                append_artist_to_file(artist_name)

                # Insert artist
                cursor.execute("INSERT OR IGNORE INTO Artists (artist_name) VALUES (?)", (artist_name,))
                cursor.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
                artist_id = cursor.fetchone()[0]

                # Insert playlist
                cursor.execute("INSERT OR IGNORE INTO Playlists (playlist_name) VALUES (?)", (playlist['name'],))
                cursor.execute("SELECT playlist_id FROM Playlists WHERE playlist_name = ?", (playlist['name'],))
                playlist_id = cursor.fetchone()[0]

                # Insert song with duration and popularity
                cursor.execute("INSERT INTO Songs (song_name, artist_id, playlist_id, spotify_track_id, popularity, duration_seconds) VALUES (?, ?, ?, ?, ?, ?)", 
                               (song_name, artist_id, playlist_id, spotify_track_id, popularity, duration_sec))
                songs_added += 1

    # Update the offset in FetchState
    cursor.execute("UPDATE FetchState SET last_playlist_offset = last_playlist_offset + 5")
    conn.commit()
    print(f"Added {songs_added} songs to the database.")   
    
##############################################################
#PLOTS   
##############################################################
def plot_average_song_duration(cursor):
    # Fetch song durations and playlist names
    cursor.execute('''
        SELECT Playlists.playlist_name, AVG(Songs.duration_seconds) as avg_duration
        FROM Songs
        JOIN Playlists ON Songs.playlist_id = Playlists.playlist_id
        GROUP BY Songs.playlist_id
    ''')
    result = cursor.fetchall()
    
    # Prepare data for plotting
    playlist_names = [row[0] for row in result]
    avg_durations = [row[1] for row in result]
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(playlist_names, avg_durations, color='skyblue')
    plt.xlabel('Playlist Name')
    plt.ylabel('Average Song Duration (seconds)')
    plt.title('Average Song Duration by Playlist')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_average_popularity(cursor):
    # Fetch average popularity and playlist names
    cursor.execute('''
        SELECT Playlists.playlist_name, AVG(Songs.popularity) as avg_popularity
        FROM Songs
        JOIN Playlists ON Songs.playlist_id = Playlists.playlist_id
        GROUP BY Songs.playlist_id
    ''')
    result = cursor.fetchall()
    
    # Prepare data for plotting
    playlist_names = [row[0] for row in result]
    avg_popularities = [row[1] for row in result]
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(playlist_names, avg_popularities, color='lightgreen')
    plt.xlabel('Playlist Name')
    plt.ylabel('Average Popularity Score')
    plt.title('Average Popularity Score by Playlist')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def fetch_city_data(cur):
    """
    Fetches average rating and average review count for each city from the database.
    """
    cur.execute('''
        SELECT c.name, AVG(r.num_rating) AS avg_rating, AVG(r.num_reviews) AS avg_reviews
        FROM restaurants AS r
        JOIN cities AS c ON r.city_id = c.city_id
        GROUP BY c.city_id
         ''')
    return cur.fetchall()

def plot_city_data(cur):
    """
    Plots a line graph showing average rating and average review count for each city.
    """
    city_data = fetch_city_data(cur)
    if city_data:
        cities = [data[0] for data in city_data]
        avg_ratings = [data[1] for data in city_data]
        avg_reviews = [data[2] for data in city_data]

        fig, ax1 = plt.subplots()

        # Plotting average rating
        color = 'tab:red'
        ax1.set_xlabel('City')
        ax1.set_ylabel('Average Rating', color=color)
        ax1.plot(cities, avg_ratings, color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        # Creating a twin object for two different y-axes on the same plot
        ax2 = ax1.twinx()  
        color = 'tab:blue'
        ax2.set_ylabel('Average Review Count', color=color)  # we already handled the x-label with ax1
        ax2.plot(cities, avg_reviews, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        # Title and layout
        plt.title('Average Rating and Review Count by City')
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
    else:
        print("No data available to plot.")
    
def plot_average_artists(cursor):
    # Fetch average popularity and playlist names
    cursor.execute('''
        SELECT AVG(age) as avg_age, COUNT()
        FROM Song\s
        JOIN Playlists ON Songs.playlist_id = Playlists.playlist_id
        GROUP BY Songs.playlist_id
    ''')
    result = cursor.fetchall()



if __name__ == '__main__':

    curry, conny = set_up_database('popularity_central.db')
    #spotified_tables(curry,conny)
    
    create_restaurants_table(curry,conny)
    create_cities_table(curry,conny)
    create_artistInfo(curry,conny)
    
    create_artistInfo(curry,conny)
    
    #add_missing_columns(curry, conny)
    url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"
    
    #fetch_and_store_data(curry,conny)
    
    # opening top 5 artist file restaurant implementation 
    with open('batched_artists_details.csv', mode='r', newline='') as file:
    # Create a CSV reader object
        artists = csv.DictReader(file)
        
    # Iterate over each row in the CSV file
        for artist in artists: # Access data by column name
        #Column headers
        #Artist Name,Begin Area,Age,Deceased
            artty_name = artist['Artist Name']
            age = artist['Age']
            
            city_name = artist['Begin Area']

            querystring = {"query":city_name,"lang":"en_US","units":"mi"}
            headers = {
            "X-RapidAPI-Key": '8e633ad51amsh4f2574b7231ca74p16b3a2jsnf0c73dc94c1f',
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
            }
            cityID_tup = city_IDs(city_name,url,headers,querystring)
            #print(cityID_tup)
            
            url2 = "https://travel-advisor.p.rapidapi.com/restaurants/list"
            
            restaurant_dict = restaurant_info(cityID_tup[0],url2,headers)
            print(restaurant_dict)
            add_cities(city_name,cityID_tup[0],curry,conny)
            add_restaurants(restaurant_dict,cityID_tup[0],curry,conny)



            
            

    #plot_average_song_duration(curry)
    #plot_city_data(curry)
    
    
    curry.close()
   