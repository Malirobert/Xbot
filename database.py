import sqlite3
from datetime import datetime

class MessageDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('message_history.db')
        self.create_table()
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()
        
    def add_message(self, username, status):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
        cursor.execute('''
            INSERT INTO messages (timestamp, username, status)
            VALUES (?, ?, ?)
        ''', (timestamp, username, status))
        self.conn.commit()
        
    def get_all_messages(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT timestamp, username, status FROM messages ORDER BY timestamp DESC')
        return cursor.fetchall()
        
    def close(self):
        self.conn.close() 