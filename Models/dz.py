import sqlite3
import datetime

import config as cfg

def getDz(date): #returns Dz array
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

def getExitstingDzDates(): #retutns dates array
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

    def forward(self, bot, user):
        bot.forward_message(user, self.dzAuhorChatId, self.dzAuthorMessageId)