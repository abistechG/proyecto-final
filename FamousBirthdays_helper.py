import requests
from bs4 import BeautifulSoup


urls = [
    'https://www.famousbirthdays.com/people/se7en.html',
    
]


with open('famous_ages.txt', 'w') as file:
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            age_tag = soup.find('a', href=lambda href: href and "/age/" in href)
            age_text = age_tag.get_text(strip=True) if age_tag else "Age information not found"
            numbers = re.findall(r'\d+', age_text)
            age_number = numbers[0] if numbers else "Age not found"
            file.write(f"{age_number}\n")
        else:
            print(f"Failed to retrieve the webpage for {url}")


urls = [
    'https://www.famousbirthdays.com/people/se7en.html',
  
]

city_counts = {}

for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        city_tag = soup.find('a', href=lambda href: href and "/city/" in href)
        city_name = city_tag.get_text(strip=True) if city_tag else "City not found"
        if city_name not in city_counts:
            city_counts[city_name] = 0
        city_counts[city_name] += 1
    else:
        print(f"Failed to retrieve the webpage for {url}")

for city, count in city_counts.items():
    print(f"{city}: {count}")

 