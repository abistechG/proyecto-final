import re
import requests
from bs4 import BeautifulSoup
import sqlite3

def scrape_data(urls):
    data = []
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
            
            # Collect data
            data.append((url.split('/')[-1].replace('.html', ''), age_number, city_name))
        else:
            print(f"Failed to retrieve the webpage for {url}")
    return data
