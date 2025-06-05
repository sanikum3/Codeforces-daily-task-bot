import sqlite3
import logging


class Database:
    def __init__(self, db_name="bot_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
        logging.info("База данных подкючена")
    
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                schedule_time TEXT DEFAULT '12:00',
                min_rating INTEGER DEFAULT 800,
                max_rating INTEGER DEFAULT 2000
            )
        ''')
        self.conn.commit()
    
    def add_group(self, chat_id):
        try:
            self.cursor.execute('''
                INSERT INTO groups (chat_id)           
                VALUES (?)
            ''', (str(chat_id),))
            self.conn.commit()
            logging.info(f"Группа {chat_id} Добавлена")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Группа {chat_id} уже существует")
            return False
    
    def get_group(self, chat_id):
        self.cursor.execute('''
            SELECT schedule_time, min_rating, max_rating
            FROM groups
            WHERE chat_id = ?                    
        ''', (str(chat_id),))
        result = self.cursor.fetchone()
        if result:
            return {
                "schedule_time": result[0],
                "min_rating": result[1],
                "max_rating": result[2],
            }
        return None
    
    def update_schedule(self, chat_id, new_time):
        self.cursor.execute('''
            UPDATE groups
            SET schedule_time = ?
            WHERE chat_id = ? 
        ''', (new_time, str(chat_id)))
        self.conn.commit()
        logging.info(f"Группа {chat_id} время изменено на {new_time}")
    
    def remove_group(self, chat_id):
        self.cursor.execute('''
            DELETE FROM groups
            WHERE chat_id = ?           
        ''', (str(chat_id),))
        self.conn.commit()
        logging.info(f"Группа {chat_id} удалена")

    def get_all_groups(self):
        self.cursor.execute('''
            SELECT chat_id, schedule_time
            FROM groups
        ''')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        logging.info("BD CLOSED")
