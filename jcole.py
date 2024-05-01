import requests

def get_restaurants(city_name, api_key):
    """
    Fetches restaurants based on the city name, retrieves each restaurant's rating, reviews, and address.
    
    Parameters:
        city_name (str): The city where the search should be performed.
        api_key (str): Yelp API key for authorization.
        
    Returns:
        list of dicts: A list of dictionaries, each containing details of a restaurant.
    """
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = 'https://api.yelp.com/v3/businesses/search'
    
    params = {
        'term': 'restaurants',
        'location': city_name,
        'limit': 5  # Adjust the limit as needed, maximum is 50
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        restaurants = response.json()['businesses']
        results = []
        for business in restaurants:
            restaurant_info = {
                'name': business['name'],
                'rating': business['rating'],
                'review_count': business['review_count'],
            }
            results.append(restaurant_info)
        return results
    else:
        raise Exception("Failed to fetch data: {} {}".format(response.status_code, response.text))

# Example usage
api_key =api_key = '-ObqIwkkSToHbYnapUZwN1Vj5ORO3WiS9Bb5GGpafTP4K0cSl6uNs__S0ebvRECjDH_ysZJHiXiW6CM5QgJIsIbfLzx0VQJJGKhAq9-SSG_21icUAEXquC45hOYxZnYx'
city_name = "Vienna"  
try:
    restaurant_data = get_restaurants(city_name, api_key)
    for restaurant in restaurant_data:
        print(f"Name: {restaurant['name']}, Rating: {restaurant['rating']}, Reviews: {restaurant['review_count']}")
except Exception as e:
    print(e)
