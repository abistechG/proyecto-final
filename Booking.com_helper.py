import requests
from dotenv import load_dotenv
import os
import sqlite3
from amadeus import Client, ResponseError 
from amadeus import Location
import json
import unittest

def cache_location(update: bool, json_cache: str, url:str, header:dict, querstring:dict):
    if update:
        json_data = None
    else:
        try:
            with open(json_cache, 'r') as file:
                json_data = json.load(file)
                print('file recieved')
                
        except:
            json_data = None
    if not json_data:
        json_data = requests.get(url, headers=header, params=querstring).json()
        with open(json_cache, 'w') as fh:
            json.dump(json_data, fh)
            
    return json_data  



if __name__ == '__main__':
   # url = "https://booking-com.p.rapidapi.com/v1/hotels/room-list"

    #querstring = {"adults_number_by_rooms":"2","checkout_date":"2024-09-20","checkin_date":"2024-09-19","units":"metric","currency":"AED","locale":"en-gb","hotel_id":"1676161,1676169"}

   # header = {
#	"X-RapidAPI-Key": "8e633ad51amsh4f2574b7231ca74p16b3a2jsnf0c73dc94c1f",
#	"X-RapidAPI-Host": "booking-com.p.rapidapi.com"     
 #   }
    
  #  data = cache_location(True, 'hotel_locations', url, header, querstring )
    
   # hotel_price = data[0]['block'][0]['incremental_price'][0]['price']
    
    #print(hotel_price)
    abys = 0
   # amadeus = Client(
    client_id= os.getenv("client_id")#,
    client_secret= os.getenv("client_secret")
#)
    # Get the access token
    auth_response = requests.post(
    'https://test.api.amadeus.com/v1/security/oauth2/token',
    data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
)

# Check if the authentication was successful
if auth_response.status_code == 200:
    access_token = auth_response.json()['access_token']

    # Use the access token to make an API call to search for a location
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Replace with the city name you are looking up
    city_name = 'Casablanca'

    # Use the "Reference Data Locations" API endpoint to search for the city
    locations_response = requests.get(
        f'https://test.api.amadeus.com/v1/reference-data/locations',
        headers=headers,
        params={'keyword': city_name, 'subType': 'CITY'}
    ) 

    if locations_response.status_code == 200:
        # Parse and display the search results
        locations_data = locations_response.json()
        for location in locations_data['data']:
            print(f"City: {location['address']['cityName']}, IATA Code: {location['iataCode']}")
    else:
        print("Failed to get location data.")
else:
    print(f"Authentication failed. Status code: {auth_response.status_code}")

    '''
try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='MAD', 
        destinationLocationCode='ATH', 
        departureDate='2024-11-01',
        adults=1)
    print(response.data)
except ResponseError as error:
    print(error)
    '''