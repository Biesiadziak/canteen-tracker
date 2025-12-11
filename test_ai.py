import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    text = """
    CZ
    🥒 Czasem to właśnie warzywo w roli głównej potrafi najlepiej "zrobić" dzień...
    Dziś serwujemy faszerowaną cukinię.
    ...
    🥩 Polędwiczki wieprzowe w sosie grzybowym
    🐖 Golonka pieczona – klasyk dla odważnych
    """
    
    prompt = f"""
    Extract the list of dishes from the following Polish canteen menu text.
    Return ONLY a JSON array of strings.
    
    Menu Text:
    {text}
    """
    
    try:
        print("Generating content...")
        response = model.generate_content(prompt)
        print("Response received.")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")
