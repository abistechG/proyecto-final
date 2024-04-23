import re
import requests
from bs4 import BeautifulSoup
import sqlite3



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
