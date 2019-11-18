import sqlite3

class DBacsessor():
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def initDB(self):
        try:
            self.cursor.execute("""
                CREATE TABLE HomeWorks
                (date text, subject text, dzAuthorId text, dzAuhorChatId text, dzAuthorMessageId text)
            """)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            pass
        
    
    def getDz(self, date):
        self.cursor.execute(f"""
            SELECT * FROM HomeWorks WHERE date = '{date}'
        """)
        return self.cursor.fetchall()
        return "err"

    def setDz(self, date, subject, dzAuthorId, dzAuhorChatId, dzAuthorMessageId):
        self.cursor.execute(f"""
            INSERT INTO HomeWorks VALUES ('{date}', '{subject}', '{dzAuthorId}', '{dzAuhorChatId}', '{dzAuthorMessageId}')
        """)#, (date, subject, dzAuthorId, dzAuhorChatId, dzAuthorMessageId))
        self.conn.commit()

    def __del__(self):
        self.conn.close()