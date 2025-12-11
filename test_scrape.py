import requests
from bs4 import BeautifulSoup

url = "https://www.facebook.com/stolowkaPP/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    if "menu" in response.text.lower():
        print("Found 'menu' in response text")
    else:
        print("'menu' not found in response text")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Title: {soup.title.string if soup.title else 'No title'}")
except Exception as e:
    print(f"Error: {e}")
