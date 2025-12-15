import sqlite3
import json
from datetime import datetime

DB_PATH = 'canteen.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            content_pl TEXT,
            content_en TEXT,
            image_urls TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_menu(date_str, content_pl, content_en, image_urls, force_update=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        if force_update:
            query = '''
                INSERT OR REPLACE INTO menus (date, content_pl, content_en, image_urls)
                VALUES (?, ?, ?, ?)
            '''
        else:
            query = '''
                INSERT INTO menus (date, content_pl, content_en, image_urls)
                VALUES (?, ?, ?, ?)
            '''
            
        c.execute(query, (date_str, content_pl, content_en, json.dumps(image_urls)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Already exists
    finally:
        conn.close()

def get_latest_menu():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM menus ORDER BY date DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "date": row['date'],
            "content_pl": row['content_pl'],
            "content_en": row['content_en'],
            "images": json.loads(row['image_urls'])
        }
    return None


def get_menu_by_date(date_str):
    """Get menu for a specific date."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM menus WHERE date = ?', (date_str,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "date": row['date'],
            "content_pl": row['content_pl'],
            "content_en": row['content_en'],
            "images": json.loads(row['image_urls'])
        }
    return None


def get_available_dates():
    """Get list of all dates that have menus."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT date FROM menus ORDER BY date DESC')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
    return None
