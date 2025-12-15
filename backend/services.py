from googletrans import Translator
import google.generativeai as genai
import os
import json

def translate_text(text):
    try:
        translator = Translator()
        # Googletrans can be unstable, wrap in try/except
        result = translator.translate(text, src='pl', dest='en')
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation unavailable"


def is_menu_post_ai(text):
    """
    Uses Google Gemini to determine if a text is a canteen menu post.
    Returns True if the text appears to be a menu, False otherwise.
    """
    if not text or len(text) < 30:
        return False
    
    # Quick heuristic check first - look for common Polish menu keywords
    menu_keywords = [
        'zupa', 'zupy', 'danie', 'dania', 'obiad', 'menu',
        'kotlet', 'filet', 'gulasz', 'pierogi', 'schabowy',
        'ziemniaki', 'surówka', 'dodatki', 'główne',
        'pomidorowa', 'rosół', 'barszcz', 'żurek'
    ]
    
    text_lower = text.lower()
    keyword_matches = sum(1 for kw in menu_keywords if kw in text_lower)
    
    # If multiple menu keywords found, likely a menu
    if keyword_matches >= 3:
        print(f"Quick heuristic: Found {keyword_matches} menu keywords - likely a menu")
        return True
    
    # Use AI for uncertain cases
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Using heuristic only.")
        return keyword_matches >= 2
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemma-3-12b-it')
        
        prompt = f"""
        Analyze the following text and determine if it is a canteen/restaurant daily menu post.
        
        A menu post typically contains:
        - List of soups (zupy)
        - List of main dishes (dania główne)
        - Side dishes or additions (dodatki)
        - Food items with descriptions
        
        Text to analyze:
        {text[:1000]}
        
        Reply with ONLY "YES" if this is a menu post, or "NO" if it's not.
        """
        
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        
        is_menu = "YES" in answer
        print(f"AI menu detection: {answer} -> {is_menu}")
        return is_menu
        
    except Exception as e:
        print(f"AI menu detection error: {e}")
        # Fall back to heuristic
        return keyword_matches >= 2


def extract_dishes_fallback(text):
    """
    Extract dishes from menu text using regex patterns.
    This is a fallback when AI extraction is not available.
    Uses googletrans for translation.
    """
    import re
    from googletrans import Translator
    
    dishes = []
    translator = Translator()
    
    # Split by lines and look for dish patterns
    lines = text.split('\n')
    
    # Skip patterns - headers and non-dish content
    skip_patterns = [
        'dzień dobry', 'zaglądacie', 'zupy:', 'dania główne:', 
        'dodatki:', 'menu', 'dziś', 'pysznego', 'obiad', 'mamy coś'
    ]
    
    for line in lines:
        # Remove emojis and clean up
        clean_line = re.sub(r'[^\w\s,ąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]', '', line).strip()
        
        if not clean_line or len(clean_line) < 4:
            continue
            
        # Skip headers and non-dish lines
        line_lower = clean_line.lower()
        if any(skip in line_lower for skip in skip_patterns):
            continue
        
        # Skip if it's just a category header
        if line_lower in ['zupy', 'dania główne', 'dodatki', 'main courses', 'soups', 'sides']:
            continue
        
        # This line looks like a dish - translate it
        try:
            result = translator.translate(clean_line, src='pl', dest='en')
            en_translation = result.text
        except Exception as e:
            print(f"Translation failed for '{clean_line}': {e}")
            en_translation = clean_line + " (Polish dish)"
        
        dishes.append({
            'pl': clean_line,
            'en': en_translation
        })
    
    print(f"Fallback extraction found {len(dishes)} dishes")
    return dishes if dishes else None


def extract_dishes_ai(text):
    """
    Uses Google Gemini to extract a list of dishes from the menu text.
    Falls back to regex extraction if GEMINI_API_KEY is not available.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Using fallback extraction.")
        return extract_dishes_fallback(text)

    try:
        genai.configure(api_key=api_key)
        # Using gemma-3-12b-it as requested (closest match to gemma-3-12b)
        model = genai.GenerativeModel('gemma-3-12b-it')
        
        prompt = f"""
        Analyze the following Polish canteen menu text and extract ALL food items available today.
        Translate each dish name into English.
        
        Rules:
        1. Return ONLY a raw JSON array of objects with "pl" and "en" keys.
           Example: [{{"pl": "Zupa pomidorowa", "en": "Tomato soup"}}, {{"pl": "Kotlet schabowy", "en": "Pork chop"}}]
        2. Extract the full name of the dish in Polish first.
        3. Translate it accurately to English.
        4. Do not include emojis, prices, or marketing fluff.
        5. Capture EVERY distinct dish listed (soups, mains, specials).
        
        Menu Text:
        {text}
        """
        
        response = model.generate_content(prompt)
        
        # Clean up response to ensure it's valid JSON
        content = response.text.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        dishes = json.loads(content)
        return dishes
        
    except Exception as e:
        print(f"AI Extraction error: {e}")
        return None

