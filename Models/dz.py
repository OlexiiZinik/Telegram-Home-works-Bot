import sqlite3
import datetime

import config as cfg

def getDz(date):
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT * FROM HomeWorks WHERE date = '{date}'""")
    conn.commit()
    ressult = cursor.fetchall()
    conn.close()
    return ressult


def getDzAfer():
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT * FROM HomeWorks""")
    conn.commit()
    ressult = []
    for dz in cursor.fetchall():
        if datetime.datetime.strptime(dz[0], "%d.%m.%Y").date() > datetime.date.today():
            ressult.append(dz)
    conn.close()
    return ressult

def isExitstsDzAfter():
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT date FROM HomeWorks""")
    conn.commit()
    ressult = []
    for dz in cursor.fetchall():
        if datetime.datetime.strptime(dz[0], "%d.%m.%Y").date() > datetime.date.today() and dz[0] not in ressult:
            ressult.append(dz[0])
    conn.close()
    return ressult


class Dz ():
    def __init__(self, date, chatId, messageId):
        #date, dzAuhorChatId, dzAuthorMessageId
        self.date = date
        self.dzAuhorChatId = chatId
        self.dzAuthorMessageId = messageId
    
    def push(self):
        conn = sqlite3.connect(cfg.DataBase)
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO HomeWorks VALUES ('{self.date}', '{self.dzAuhorChatId}', '{self.dzAuthorMessageId}')
        """)
        conn.commit()
        conn.close()