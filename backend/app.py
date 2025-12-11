from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import schedule
import time
import threading
from scraper import check_for_new_menu
from models import init_db, get_latest_menu
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize DB
init_db()

# Background scheduler for checking menu
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

schedule.every(30).minutes.do(check_for_new_menu)
t = threading.Thread(target=run_schedule)
t.daemon = True
t.start()

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    menu = get_latest_menu()
    if menu:
        return jsonify(menu)
    return jsonify({"error": "No menu found"}), 404

@app.route('/api/check-now', methods=['POST'])
def force_check():
    force = request.json.get('force', False) if request.is_json else False
    result = check_for_new_menu(force=force)
    return jsonify({"status": "checked", "new_found": result})

if __name__ == '__main__':
    # Run initial check on startup
    check_for_new_menu()
    app.run(host='0.0.0.0', port=8000)
