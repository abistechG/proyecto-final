import requests
import os
import time
import json
import unittest

def cache_location(update: bool, json_cache: str, url:str, header:dict, querstring:dict):
    '''
    stores read in json data into a local file, updates it upon request
    '''
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

def city_IDs(city_name: str, url: str, headers: dict, update = False):
    '''
    finds the city id of the passed in city name\n
    stores the data into a file\n
    returns a tuple with the city id,file name
    '''
    
    file_name = f"locations_{city_name}"
    
    data = cache_location(update, file_name, url, headers, querystring )
    
    location_id = data['data']['Typeahead_autocomplete']['results'][0]['detailsV2']['locationId']
    
    return (location_id,file_name)

def restaurant_info(location_id:int, url: str, headers: dict):
    '''
    parses all restaurant data from 4 separate pages \n
    restaurants are from given location id \n
    returns a nested dictionary of the restaurant's name, rating, and number of reviews
    '''
    
    restaurants = {}
    file_name = f"restaurants in {location_id}"
    
    offsets = ['0','30', '60', '90']  #ignores this amount of data, max output per "page" is 30
    for offset in offsets: #changes pages
        file_name = f"restaurants in {location_id}, {offset}" 
        querystring = {"location_id":str(location_id),"restaurant_tagcategory":"10591","restaurant_tagcategory_standalone":"10591","currency":"USD","lunit":"mi","limit":"30","open_now":"false","offset":offset,"lang":"en_US"}

        time.sleep(1)  #delay time between calls
        data = cache_location(False, file_name, url, headers, querystring)
        
        restaurant_name  = data['data'][0]['name'] 
        num_reviews = data['data'][0]['num_reviews']
        restaurant_rating = data['data'][0]['rating']
        restaurants[restaurant_name]['rating'] = restaurant_rating
        restaurants[restaurant_name]['number of reviews'] = num_reviews
    
    return restaurants    
         
    
    
    
    
    

if __name__ == '__main__':
    url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"
    city_name = "Casablanca"

    querystring = {"query":city_name,"lang":"en_US","units":"mi"}
    headers = {
	"X-RapidAPI-Key": os.getenv('API_KEY'),
	"X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
}
    file_name = f"locations_{city_name}"
    data = cache_location(False, file_name, url, headers, querystring )
    
    location_id = data['data']['Typeahead_autocomplete']['results'][0]['detailsV2']['locationId']
    
    print(type(data))
    
    url = "https://travel-advisor.p.rapidapi.com/restaurants/list"

    querystring = {"location_id":str(location_id),"restaurant_tagcategory":"10591","restaurant_tagcategory_standalone":"10591","currency":"USD","lunit":"mi","limit":"30","open_now":"false","offset":"0","lang":"en_US"}

    file2_name = "restaurants_list"
    data2 = cache_location(False, file2_name, url, headers, querystring )
    
    num_reviews = data2['data'][0]['num_reviews']
    restaurant_rating = data2['data'][0]['rating']
    print(num_reviews)
    print(restaurant_rating)