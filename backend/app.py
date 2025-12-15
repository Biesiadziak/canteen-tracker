from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import schedule
import time
import threading
from scraper import check_for_new_menu
from models import init_db, get_latest_menu, get_menu_by_date, get_available_dates
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
    # Check if a specific date is requested
    date = request.args.get('date')
    if date:
        menu = get_menu_by_date(date)
    else:
        menu = get_latest_menu()
    
    if menu:
        return jsonify(menu)
    return jsonify({"error": "No menu found"}), 404


@app.route('/api/dates', methods=['GET'])
def get_dates():
    """Get list of all available menu dates."""
    dates = get_available_dates()
    return jsonify({"dates": dates})

@app.route('/api/check-now', methods=['POST'])
def force_check():
    force = request.json.get('force', False) if request.is_json else False
    result = check_for_new_menu(force=force)
    return jsonify({"status": "checked", "new_found": result})

if __name__ == '__main__':
    # Run initial check in background thread so server starts quickly
    def initial_check():
        time.sleep(2)  # Wait for server to be ready
        check_for_new_menu()
    
    init_thread = threading.Thread(target=initial_check)
    init_thread.daemon = True
    init_thread.start()
    
    app.run(host='0.0.0.0', port=8000)
