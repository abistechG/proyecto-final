import requests
import os
import sqlite3
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
    url = "https://booking-com.p.rapidapi.com/v1/hotels/room-list"

    querstring = {"adults_number_by_rooms":"3,1","checkout_date":"2024-09-15","checkin_date":"2024-09-14","units":"metric","currency":"AED","locale":"en-gb","hotel_id":"1676161","children_ages":"5,0,9","children_number_by_rooms":"2,1"}

    header = {
	"X-RapidAPI-Key": "8e633ad51amsh4f2574b7231ca74p16b3a2jsnf0c73dc94c1f",
	"X-RapidAPI-Host": "booking-com.p.rapidapi.com"     
    }
    
    data = cache_location(True, 'hotel_locations', url, header, querstring )
    
    print(data)