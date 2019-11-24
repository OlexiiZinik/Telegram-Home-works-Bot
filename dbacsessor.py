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

# class DBacsessor():
#     def __init__(self, dbname):
#         self.dbname = dbname
#         self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
#         self.cursor = self.conn.cursor()
    
    
        
    
    # def getDz(self, date):
    #     self.cursor.execute(f"""
    #         SELECT * FROM HomeWorks WHERE date = '{date}'
    #     """)
    #     return self.cursor.fetchall()
    #     return "err"

    # def setDz(self, date, dzAuhorChatId, dzAuthorMessageId):
    #     self.cursor.execute(f"""
    #         INSERT INTO HomeWorks VALUES ('{date}', '{dzAuthorId}', '{dzAuthorMessageId}')
    #     """)
    #     self.conn.commit()

    # def __del__(self):
    #     self.conn.close()