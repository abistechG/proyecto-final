import sqlite3
import os
from restaurants_helper import cache_location, city_IDs, restaurant_info
from Spotipy_helper import fetch_diverse_playlists, display_playlist_details
import re
import requests
from bs4 import BeautifulSoup


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
    
    cur.execute("DROP TABLE IF EXISTS restaurants")
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
    cur.execute("DROP TABLE IF EXISTS cities")
    cur.execute('''CREATE TABLE IF NOT EXISTS cities (
        city_id INTEGER,
        name TEXT
    )
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


def add_restaurants(restaurants:dict, city_id:int, cur, conn):
    '''
    adds restaurant data from dictionary (restaurant_info) and puts 
    on restaurant data table
    '''
    
    for key, keys2 in restaurants.items():
        valuesVec = []
        for k, values in keys2.items():
            valuesVec.append(values)
            
        cur.execute('''
                    INSERT INTO restaurants (name,num_reviews,num_rating,city_id)
                    VALUES (?,?,?,?)
                    ''',
                    (key,valuesVec[0],valuesVec[1],city_id))    
    conn.commit()

 #Musica
 # Connect to the SQLite database
conn = sqlite3.connect('music.db')
cursor = conn.cursor()

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
def fetch_and_store_data():
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

                # Insert artist
                cursor.execute("INSERT OR IGNORE INTO Artists (artist_name) VALUES (?)", (artist_name,))
                cursor.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
                artist_id = cursor.fetchone()[0]

                # Insert playlist
                cursor.execute("INSERT OR IGNORE INTO Playlists (playlist_name) VALUES (?)", (playlist['name'],))
                cursor.execute("SELECT playlist_id FROM Playlists WHERE playlist_name = ?", (playlist['name'],))
                playlist_id = cursor.fetchone()[0]

                # Insert song
                cursor.execute("INSERT INTO Songs (song_name, artist_id, playlist_id, spotify_track_id) VALUES (?, ?, ?, ?)", 
                               (song_name, artist_id, playlist_id, spotify_track_id))
                songs_added += 1

    # Update the offset in FetchState
    cursor.execute("UPDATE FetchState SET last_playlist_offset = last_playlist_offset + 5")
    conn.commit()
    print(f"Added {songs_added} songs to the database.")   
    
    
    
 
    

if __name__ == '__main__':
    
    fetch_and_store_data()
    
   
    #setup_spotty_database()
    #genres = ['hip-hop', 'party', 'k-pop', 'jazz', 'classical']
    
    
    curry, conny = set_up_database('restaurants.db')
    
    create_restaurants_table(curry,conny)
    
    curry1, conny1 = set_up_database('cities.db')
    
    create_cities_table(curry1,conny1)
    
    url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"
    city_name = "Casablanca"

    querystring = {"query":city_name,"lang":"en_US","units":"mi"}
    headers = {
	"X-RapidAPI-Key": os.getenv('API_KEY'),
	"X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
}
    cityID_tup = city_IDs(city_name,url,headers,querystring)
    #print(cityID_tup)
    
    url2 = "https://travel-advisor.p.rapidapi.com/restaurants/list"
    
    restaurant_dict = restaurant_info(cityID_tup[0],url2,headers)
    #print(len(restaurant_dict))
    
    add_cities(city_name,cityID_tup[0],curry1,conny1)
    
    add_restaurants(restaurant_dict,cityID_tup[0],curry,conny)
    
    
    ### FamousBirthdays_helper.py ### START ###
    '''
    print('checkpoint 0')
    conn = sqlite3.connect("Famous.db")
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS FamousPeople (name TEXT, age INTEGER, city TEXT)')
    print('checkpoint 1')
    urls = ['https://www.famousbirthdays.com/people/se7en.html']  # Add more URLs as needed

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Fetching the age
            age_tag = soup.find('a', href=lambda href: href and "/age/" in href)
            age_text = age_tag.get_text(strip=True) if age_tag else "Age information not found"
            numbers = re.findall(r'\d+', age_text)
            age_number = int(numbers[0]) if numbers else None
            
            # Fetching the city
            city_tag = soup.find('a', href=lambda href: href and "/city/" in href)
            city_name = city_tag.get_text(strip=True) if city_tag else "City not found"
            
            # Insert data into the database
            cur.execute('INSERT INTO FamousPeople (name, age, city) VALUES (?, ?, ?)', 
                        (url.split('/')[-1].replace('.html', ''), age_number, city_name))
        else:
            print(f"Failed to retrieve the webpage for {url}")
    print('checkpoint 2')
    # Commit changes and close the database connection
    conn.commit()
    #conn.close()
    print('checkpoint 3')
    # Output city counts
    #cur = conn.cursor()
    cur.execute('SELECT city, COUNT(*) FROM FamousPeople GROUP BY city')
    print('checkpoint 4')
    city_counts = cur.fetchall()
    for city, count in city_counts:
        print(f"{city}: {count}")
    print('checkpoint 5')
    cur.close() 
    print('checkpoint 6')

    ### FamousBirthdays_helper.py ### END ###
'''
conn.close()
