import re
import requests
from bs4 import BeautifulSoup

url = 'https://www.famousbirthdays.com/people/earlan-bartley.html'


response = requests.get(url)


if response.status_code == 200:
    html_content = response.text
else:
    print("Failed to retrieve the webpage")
    html_content = ""

soup = BeautifulSoup(html_content, 'html.parser')
age_tag = soup.find('a', href=lambda href: href and "/age/" in href)
age_text = age_tag.get_text(strip=True) if age_tag else "Age information not found"


#print(soup.prettify())  

numbers = re.findall(r'\d+', age_text)

age_number = numbers[0] if numbers else "Age not found"
