import sqlite3

import config as cfg

def initDB():
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE HomeWorks
            (date text, dzAuhorChatId text, dzAuthorMessageId text)
        """)
        conn.commit()
    except sqlite3.OperationalError as e:
        pass
    conn.close()