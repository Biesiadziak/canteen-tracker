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

def extract_dishes_ai(text):
    """
    Uses Google Gemini to extract a list of dishes from the menu text.
    Requires GEMINI_API_KEY environment variable.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Skipping AI extraction.")
        return None

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

