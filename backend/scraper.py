import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from services import translate_text, extract_dishes_ai
from models import save_menu
import re
from facebook_scraper import get_posts

# Note: Scraping Facebook directly is difficult due to dynamic content and login walls.
# This is a simplified scraper that attempts to get public page content.
# For a production app, you would likely need the Facebook Graph API or a library like 'facebook-scraper' with cookies.

FB_PAGE_ID = "stolowkaPP"

def check_for_new_menu(force=False):
    print(f"Checking for new menu (force={force})...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # SKIP FACEBOOK SCRAPING - IT IS UNRELIABLE WITHOUT COOKIES
    # Using the fallback text provided by the user directly.
    print("Using fallback/mock data directly (Scraping disabled).")
    scraped_text_pl = """
CZ
🥒 Czasem to właśnie warzywo w roli głównej potrafi najlepiej "zrobić" dzień, rozluźnić myśli i sprawić, że wszystko – choćby na chwilę – wskakuje na swoje miejsce.
Dziś serwujemy faszerowaną cukinię.
Miękką, pieczoną, z nadzieniem tak treściwym, że nawet najwięksi fani karkówki przyznają:
👉 „No dobra, to ma sens.”
Bo dobry comfort food nie musi kapać tłuszczem i spoczywać na górze ziemniaków.
Czasem to po prostu dobrze przyprawione, ciepłe, miękkie w środku i chrupiące z wierzchu warzywo.
🌿 A jeśli szukasz czegoś innego – też nie będziesz zawiedziony:
🥩 Polędwiczki wieprzowe w sosie grzybowym
🐖 Golonka pieczona – klasyk dla odważnych
🐓 Żołądki drobiowe w sosie koperkowym
🍗 Noga z kurczaka 
🥣 Zupa? Krem ziemniaczany z imbirem i gruszką – nasz rozgrzewający znak firmowy 🔥
🥗 Dodatki: ziemniaki, ryż z warzywami, warzywo na ciepło, surówki
    """

    # 1. Translate
    print("Translating...")
    translated_text = translate_text(scraped_text_pl)
    
    # 2. Extract Dishes (AI Only)
    print("Extracting dishes...")
    
    dishes = extract_dishes_ai(scraped_text_pl)
    
    if not dishes:
        print("AI extraction failed. Returning empty list.")
        dishes = []
    
    # dishes is now a list of objects: [{"pl": "...", "en": "..."}]
    # We store this directly as the "images" data structure for now
    images_data = dishes
            
    # 3. Save
    is_new = save_menu(today, scraped_text_pl, translated_text, images_data, force_update=force)
    
    if is_new:
        print(f"New menu saved for {today}")
        return True
    else:
        print("Menu for today already exists.")
        return False

# Real implementation note:
# To scrape FB properly, you might use:
# from facebook_scraper import get_posts
# for post in get_posts('stolowkaPP', pages=1):
#     text = post['text']
#     ... process text ...
