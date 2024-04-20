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


<<<<<<< Updated upstream
#print(soup.prettify())  

numbers = re.findall(r'\d+', age_text)
=======
age_span = soup.find('span', string =lambda text: text and 'Age' in text)
age_info = age_span.find('a') if age_span else None
>>>>>>> Stashed changes

age_number = numbers[0] if numbers else "Age not found"
