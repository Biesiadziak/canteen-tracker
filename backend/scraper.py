import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import re
from services import translate_text, extract_dishes_ai, is_menu_post_ai
from models import save_menu

FB_PAGE_ID = "stolowkaPP"
FB_URL = f"https://www.facebook.com/{FB_PAGE_ID}/"


def find_all_posts_recursive(obj, posts=None):
    """
    Recursively search through Facebook's JSON data to find all posts.
    Returns a list of post objects containing text and timestamp.
    """
    if posts is None:
        posts = []
    
    if isinstance(obj, dict):
        # Check for story-like structure with message text
        if 'message' in obj and isinstance(obj['message'], dict) and 'text' in obj['message']:
            text = obj['message']['text']
            # Get timestamp from various possible fields
            timestamp = (obj.get('creation_time') or 
                        obj.get('publish_time') or 
                        obj.get('created_time'))
            
            # Only add if text has meaningful content (more than 20 chars)
            if text and len(text) > 20:
                posts.append({
                    'text': text,
                    'timestamp': timestamp
                })
        
        # Continue searching in nested objects
        for k, v in obj.items():
            find_all_posts_recursive(v, posts)
            
    elif isinstance(obj, list):
        for item in obj:
            find_all_posts_recursive(item, posts)
    
    return posts


def find_key_recursive(obj, key, target_value_substring=None):
    """Find a key in nested JSON, optionally matching a substring."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                if target_value_substring:
                    if isinstance(v, str) and target_value_substring in v:
                        return v
                else:
                    return v
            result = find_key_recursive(v, key, target_value_substring)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_key_recursive(item, key, target_value_substring)
            if result:
                return result
    return None


def extract_all_text_blocks(obj, texts=None, min_length=50):
    """
    Extract all text blocks from the JSON data.
    Returns unique texts that are likely to be post content.
    """
    if texts is None:
        texts = set()
    
    if isinstance(obj, dict):
        # Look for 'text' keys with substantial content
        if 'text' in obj and isinstance(obj['text'], str):
            text = obj['text']
            if len(text) >= min_length:
                texts.add(text)
        
        for v in obj.values():
            extract_all_text_blocks(v, texts, min_length)
            
    elif isinstance(obj, list):
        for item in obj:
            extract_all_text_blocks(item, texts, min_length)
    
    return texts


def scrape_facebook_posts():
    """
    Scrape Facebook page and extract all recent posts.
    Returns a list of post dictionaries with 'text' and 'timestamp' keys.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    
    posts = []
    
    try:
        print(f"Fetching {FB_URL}...")
        response = requests.get(FB_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch Facebook page: {response.status_code}")
            return posts

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        seen_texts = set()  # To avoid duplicate posts
        
        for script in scripts:
            if not script.string:
                continue
                
            try:
                data = json.loads(script.string)
                
                # Method 1: Find posts with message structure
                found_posts = find_all_posts_recursive(data)
                for post in found_posts:
                    if post['text'] not in seen_texts:
                        seen_texts.add(post['text'])
                        posts.append(post)
                
                # Method 2: Extract all substantial text blocks as fallback
                text_blocks = extract_all_text_blocks(data)
                for text in text_blocks:
                    if text not in seen_texts:
                        seen_texts.add(text)
                        posts.append({
                            'text': text,
                            'timestamp': None
                        })
                        
            except json.JSONDecodeError:
                continue
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping Facebook: {e}")
        
    print(f"Found {len(posts)} potential posts")
    return posts


def is_post_from_today(timestamp):
    """Check if a Unix timestamp corresponds to today's date."""
    if not timestamp:
        return None  # Unknown
    
    try:
        post_date = datetime.fromtimestamp(timestamp)
        return post_date.date() == datetime.now().date()
    except:
        return None


def find_today_menu_post(posts):
    """
    Find the most likely menu post from today.
    Returns the post text if found, None otherwise.
    """
    today_posts = []
    unknown_date_posts = []
    
    for post in posts:
        text = post.get('text', '')
        timestamp = post.get('timestamp')
        
        is_today = is_post_from_today(timestamp)
        
        if is_today is True:
            today_posts.append(post)
        elif is_today is None:
            # Unknown date - could be from today
            unknown_date_posts.append(post)
    
    print(f"Posts from today: {len(today_posts)}")
    print(f"Posts with unknown date: {len(unknown_date_posts)}")
    
    # First, check today's posts for menu content
    for post in today_posts:
        text = post.get('text', '')
        print(f"Checking today's post ({len(text)} chars)...")
        
        # Use AI to determine if this is a menu post
        if is_menu_post_ai(text):
            print("Found menu post from today!")
            return text
    
    # If no dated posts found, check unknown date posts
    # (These might be from today but without timestamp info)
    for post in unknown_date_posts:
        text = post.get('text', '')
        print(f"Checking undated post ({len(text)} chars)...")
        
        if is_menu_post_ai(text):
            print("Found potential menu post (date unknown)!")
            return text
    
    return None

def check_for_new_menu(force=False):
    """
    Check for new menu posts on Facebook.
    
    1. Scrape all recent posts from the Facebook page
    2. Find posts from today
    3. Use AI to determine if any post is a menu
    4. If found, extract dishes and save
    """
    print(f"Checking for new menu (force={force})...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Scrape all posts from Facebook
    posts = scrape_facebook_posts()
    
    menu_found = False
    scraped_text_pl = None
    
    if not posts:
        print("No posts found on Facebook page.")
    else:
        # Find today's menu post
        scraped_text_pl = find_today_menu_post(posts)
        
        if scraped_text_pl:
            menu_found = True
            print(f"Menu found! ({len(scraped_text_pl)} chars)")
        else:
            print("No menu post found for today.")

    # If no menu found, don't overwrite existing good data
    if not menu_found:
        from models import get_latest_menu
        existing = get_latest_menu()
        if existing and existing.get('date') == today and "Nie znaleziono" not in existing.get('content_pl', ''):
            print("Keeping existing menu - no new menu found to replace it.")
            return False
        
        # Only save "not found" message if we don't have a good menu for today
        scraped_text_pl = "Nie znaleziono dzisiejszego menu"

    # 1. Translate
    print("Translating...")
    translated_text = translate_text(scraped_text_pl)
    
    # 2. Extract Dishes - only if we found a menu
    print("Extracting dishes...")
    
    dishes = []
    if menu_found:
        dishes = extract_dishes_ai(scraped_text_pl)
        if not dishes:
            print("Dish extraction returned empty. Using empty list.")
            dishes = []
    
    images_data = dishes
            
    # 3. Save
    is_new = save_menu(today, scraped_text_pl, translated_text, images_data, force_update=force)
    
    if is_new:
        print(f"New menu saved for {today}")
        return True
    else:
        print("Menu for today already exists.")
        return False
