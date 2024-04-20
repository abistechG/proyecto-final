import requests
from bs4 import BeautifulSoup

url = 'https://www.famousbirthdays.com/people/earlan-bartley.html'


response = requests.get(url)


if response.status_code == 200:
    html_content = response.text
else:
    print("Failed to retrieve the webpage")
    html_content = ""

soup = BeautifulSoup(html_content, 'lxml')



age_span = soup.find('span', string =lambda text: text and 'Age' in text)
age_info = age_span.find('a') if age_span else None


if age_info:
    print(age_info.text.strip())  
else:
    print("Age information not found")