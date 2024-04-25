import sqlite3
import os
from Spotipy_helper import get_artist_names_by_genre 
from restaurants_helper import cache_location, city_IDs, restaurant_info
import re
import requests
from bs4 import BeautifulSoup


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
                    VALUES (?,?,?)
                    ''',
                    (key,valuesVec[0],valuesVec[1],city_id))    

    
    
    
    
 
    

if __name__ == '__main__':
    setup_database()
    genres = ['hip-hop', 'party', 'k-pop', 'jazz', 'classical']
    
    ### FamousBirthdays_helper.py ### START ###
    
conn = sqlite3.connect("Famous.db")
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS FamousPeople (name TEXT, age INTEGER, city TEXT)')

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

# Commit changes and close the database connection
conn.commit()
conn.close()

# Output city counts
cur = conn.cursor()
cur.execute('SELECT city, COUNT(*) FROM FamousPeople GROUP BY city')
city_counts = cur.fetchall()
for city, count in city_counts:
    print(f"{city}: {count}")

cur.close() 

### FamousBirthdays_helper.py ### END ###
    
