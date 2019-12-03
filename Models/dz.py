import sqlite3
import datetime

import config as cfg

def getDz(date): #returns existing HM array
    try:
        d = datetime.datetime.strptime(date, "%d.%m.%Y")
    except:
        raise InvalidDateException()
        return
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT * FROM HomeWorks WHERE date = '{date}'""")
    conn.commit()
    ressult = []
    for response in cursor.fetchall():
        ressult.append(Dz(response[0], response[1], response[2]))
    conn.close()
    return ressult

def getExitstingDzDates(): #returns dates array, which were reserved in DB 
    conn = sqlite3.connect(cfg.DataBase)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT date FROM HomeWorks""")
    conn.commit()
    ressult = []
    for dz in cursor.fetchall():
        if datetime.datetime.strptime(dz[0], "%d.%m.%Y").date() > datetime.date.today() and datetime.datetime.strptime(dz[0], "%d.%m.%Y").date() not in ressult:
            ressult.append(datetime.datetime.strptime(dz[0], "%d.%m.%Y").date())
    conn.close()
    return ressult


def validDate(date):
    try:
        d = datetime.datetime.strptime(date, "%d.%m.%Y")
    except:
        raise InvalidDateException()

class InvalidDateException(Exception):
    pass

# Home work object
class Dz ():
    def __init__(self, date, chatId, messageId):
        #date, dzAuhorChatId, dzAuthorMessageId
        self.date = date
        self.dzAuhorChatId = chatId
        self.dzAuthorMessageId = messageId
    
    # Method which pushes home work (Telegram message pointer) into DB
    def push(self):
        conn = sqlite3.connect(cfg.DataBase)
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO HomeWorks VALUES ('{self.date}', '{self.dzAuhorChatId}', '{self.dzAuthorMessageId}')
        """)
        conn.commit()
        conn.close()
    # Method which sends HM via Tegram forward message()
    def forward(self, bot, user):
        bot.forward_message(user, self.dzAuhorChatId, self.dzAuthorMessageId)