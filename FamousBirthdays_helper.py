import requests
from datetime import datetime
import csv

def calculate_age(birthdate, deathdate=None):
    if deathdate:
        return deathdate.year - birthdate.year - ((deathdate.month, deathdate.day) < (birthdate.month, birthdate.day))
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def get_artists_details(artist_names):
    artist_details = {}  # Dictionary to store details of each artist
    url = "https://musicbrainz.org/ws/2/artist/"
    params = {'fmt': 'json'}

    for artist_name in artist_names:
        params['query'] = 'artist:' + artist_name
        response = requests.get(url, params=params)
        data = response.json()

        if 'artists' in data and data['artists']:
            artist = data['artists'][0]  # Assuming the first result is the most relevant
            birth_date_str = artist.get('life-span', {}).get('begin', None)
            death_date_str = artist.get('life-span', {}).get('end', None)
            age = 'Unknown'  # Default if no birth date is available or if it's incomplete
            deceased = 'No'  # Default to 'No' unless an end date is found

            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
                    if death_date_str:
                        death_date = datetime.strptime(death_date_str, '%Y-%m-%d')
                        age = calculate_age(birth_date, death_date)
                        deceased = 'Yes'
                    else:
                        age = calculate_age(birth_date)
                except ValueError:
                    continue  # Skip adding this artist if the date is incomplete or improperly formatted

            if age != 'Unknown':
                artist_details[artist['name']] = {
                    'Begin Area': artist.get('begin-area', {}).get('name', 'Unknown'),
                    'Age': age,
                    'Deceased': deceased
                }

    return artist_details

def write_artist_details_to_csv(artist_details, filename='batched_artists_details.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Artist Name', 'Begin Area', 'Age', 'Deceased'])  # Header
        for artist, details in artist_details.items():
            if details['Age'] != 'Unknown' and details['Begin Area'] != 'Artist not found' and details['Age'] != 'Artist not found' and details['Deceased'] != 'Artist not found':
                writer.writerow([artist, details['Begin Area'], details['Age'], details['Deceased']])

def extract_batched_artists(artist_names):
    batched_artists = []
    index = 0
    while index < len(artist_names):
        batched_artists.extend(artist_names[index:index+5])
        index += 25  
    return batched_artists

if __name__ == '__main__':
    with open('artists.txt', 'r', encoding='utf-8') as file:
        artist_names = [line.strip() for line in file if line.strip()]
    batched_artists = extract_batched_artists(artist_names)
    artist_details = get_artists_details(batched_artists)
    write_artist_details_to_csv(artist_details)
    print("Batched artist details have been written to 'batched_artists_details.csv'")
