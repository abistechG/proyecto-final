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
                #print('file recieved')
                
        except:
            json_data = None
    if not json_data:
        json_data = requests.get(url, headers=header, params=querstring).json()
        with open(json_cache, 'w') as fh:
            json.dump(json_data, fh)
            
    return json_data  

def find_key(data, target):
    """
    Recursively search for the target key in the JSON data.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target:
                return value
            result = find_key(value, target)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_key(item, target)
            if result is not None:
                return result
    return None

def city_IDs(city_name: str, url: str, headers: dict, querystring:str, update = False):
    '''
    finds the city id of the passed in city name\n
    stores the data into a file\n
    returns a tuple with the city id,file name
    '''
    
    file_name = f"locations_{city_name}"
    
    data = cache_location(update, file_name, url, headers, querystring)
    
    locate = data['data']['Typeahead_autocomplete']['results']
    
    for entry in locate:
        details_v2 = entry.get('detailsV2', {})
        location_id = details_v2.get('locationId')
        if location_id:
            return (location_id, file_name)
    
    return None


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
        
        
        
        if 'data' in data and isinstance(data['data'], list):
            i = 0
            while i < len(data['data']):
                # Check if 'name' key exists in the restaurant data
                if 'name' in data['data'][i]:
                    restaurant_name = data['data'][i]['name']
                    num_reviews = data['data'][i].get('num_reviews', 0)  # Default to 0 if 'num_reviews' doesn't exist
                    restaurant_rating = data['data'][i].get('rating', 0)  # Default to 0 if 'rating' doesn't exist
                    
                    # Add restaurant data to the dictionary
                    restaurants[restaurant_name] = {
                        'rating': restaurant_rating,
                        'number of reviews': num_reviews
                    }
                
                i += 1
    
    return restaurants    
         
    
    
    
    
    

if __name__ == '__main__':
    url = "https://travel-advisor.p.rapidapi.com/locations/v2/auto-complete"
    city_name = "Detroit"

    querystring = {"query":city_name,"lang":"en_US","units":"mi"}
    headers = {
	"X-RapidAPI-Key": '8e633ad51amsh4f2574b7231ca74p16b3a2jsnf0c73dc94c1f',
	"X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
}
    file_name = f"locations_{city_name}"
    data = cache_location(False, file_name, url, headers, querystring )
    
   # location_id = data['data']['Typeahead_autocomplete']['results'][0]['detailsV2']['locationId']
    
    #print(type(data))
    tups = city_IDs(city_name,url,headers,querystring)
    print(tups)
    
    
    
    #url2 = "https://travel-advisor.p.rapidapi.com/restaurants/list"

    #checkDIct = restaurant_info(tups[0],url2,headers)
    #print('blank')
    #print('blank')
    #print('blank')
    #print(len(checkDIct))
    
    #querystring = {"location_id":str(location_id),"restaurant_tagcategory":"10591","restaurant_tagcategory_standalone":"10591","currency":"USD","lunit":"mi","limit":"30","open_now":"false","offset":"0","lang":"en_US"}

    
    
    '''
    file2_name = "restaurants_list"
    data2 = cache_location(False, file2_name, url, headers, querystring )
    
    num_reviews = data2['data'][0]['num_reviews']
    restaurant_rating = data2['data'][0]['rating']
    print(num_reviews)
    print(restaurant_rating)
    '''