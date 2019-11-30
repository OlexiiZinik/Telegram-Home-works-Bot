import telebot
import re
import datetime
import logging
import sys
from telebot import types

import Models.dz
import dbacsessor
import Models.UI
import config as cfg
import MISC.events

bot = telebot.TeleBot(cfg.Token)

logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
ch = [logging.StreamHandler(sys.stdout),logging.FileHandler("bot.log", mode='a')]
logger.addHandler(ch[0])
logger.addHandler(ch[1])
logger.setLevel(logging.INFO)
ch[0].setFormatter(formatter)
ch[1].setFormatter(formatter)

evntStatus = MISC.events.EventStatus()


def logMessage(message, callback=False):
    if callback:
       logger.log(logging.INFO, str(message.from_user.first_name) + " @ " + str(message.from_user.id) + " on " + str(message.message.chat.id) + " callback : " + message.data)
    else:
       logger.log(logging.INFO, str(message.from_user.first_name) + " @ " + str(message.from_user.id) + " on " + str(message.chat.id) + " " + message.content_type + " : " + message.text)


@bot.message_handler(commands=['start', 'help'])
def startMessage(message):
    logMessage(message)
    if message.text == "/start":
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nЭтот бот поможет нам с дз)\nПреступим!')
    bot.send_message(message.chat.id, """
/help - Показывает это сообщение
/get_dz - Возвращает дз на определенную дату
/set_dz - Добавляет дз на определенную дату""")



@bot.message_handler(regexp="/get_dz \d\d.\d\d.\d\d\d\d")
def onGetDz(message):
    logMessage(message)
    #Handling Exception, wich would be thrown gives us invalid date like 44.13.2014 
    try:
        for dz in Models.dz.getDz(message.text[8:]):
            dz.forward(bot, message.chat.id)
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /get_dz (день.месяц.год)\nПример /get_dz 01.11.2019")




@bot.callback_query_handler(func = lambda call: re.match("/get_dz \d\d.\d\d.\d\d\d\d", call.data))
def onGetDzCallback(call):
    logMessage(call, callback=True)
    #I'm dont handling exeptions because user can't get acces to this method
    bot.send_message(call.message.chat.id, f"Дз на {call.data[8:13]}")
    for dz in Models.dz.getDz(call.data[8:]): 
        dz.forward(bot, call.message.chat.id)
    

@bot.message_handler(commands=["get_dz"])
def onGetDzWithOutDate(message):
    logMessage(message)
    Models.UI.getDz(bot, message.chat.id)

#=========================================================

@bot.message_handler(regexp="/set_dz \d\d.\d\d.\d\d\d\d")
def onSetDz(message):
    logMessage(message)
    #Handling Exception, wich would be thrown gives us invalid date like 44.13.2014 
    try:
        Models.dz.validDate(message.text[8:])
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /set_dz (день.месяц.год)\nПример /set_dz 01.11.2019")
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
    bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text[8:13]}', reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzAuthor = message.from_user.id
    evntStatus.settingDzDate = message.text[8:]


@bot.message_handler(commands=["set_dz"])
def onSetDzWithOutDate(message):
    logMessage(message)
    Models.UI.setDz(bot, message.chat.id)


@bot.callback_query_handler(func = lambda call: re.match("/set_dz \d\d.\d\d.\d\d\d\d", call.data))
def onSetDzCallback(call):
    logMessage(call, callback=True)
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
    #bot.edit_message_text(f'{call.from_user.first_name}, Вы добавляете дз на {call.data[8:13]}', reply_markup=keyboard)
    bot.edit_message_text(f'{call.from_user.first_name}, Вы добавляете дз на {call.data[8:13]}', call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    #bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzAuthor = call.from_user.id
    evntStatus.settingDzDate = call.data[8:]


@bot.callback_query_handler(func=lambda call: call.data == "/setDzWithDate")
def onSetDzWithDateCallback(call):
    logMessage(call, callback=True)
    bot.edit_message_text("Укажите дату\n(день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019", call.message.chat.id, call.message.message_id, reply_markup=None)
    #bot.send_message(call.message.chat.id, "Укажите дату\n(день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
    def getDate(message):
        logMessage(message)
        global evntStatus
        datestr = ""
        if re.match("\d\d.\d\d.\d\d\d\d", message.text):
            datestr = message.text
        elif re.match("\d\d.\d\d", message.text):
            datestr = message.text+"."+str(datetime.datetime.today().year)
        else:
            bot.send_message(message.chat.id, "Не правельно!\nукажите (день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
            bot.register_next_step_handler_by_chat_id(message.chat.id, getDate)
            return
        try:
            Models.dz.validDate(datestr)
        except Models.dz.InvalidDateException:
            bot.send_message(message.chat.id, "Не правельно!\nукажите (день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
            bot.register_next_step_handler_by_chat_id(message.chat.id, getDate)
            return
        #If anything goes wrong we interrupt method, say user that he is an idiot and register next message handler, again ...
        #Else user can send home works
        evntStatus.settingDzDate = datestr
        evntStatus.settingDzAuthor = message.from_user.id
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {datestr}', reply_markup=keyboard)

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, getDate)
    evntStatus.settingDz = True


@bot.message_handler(commands=['done'])
def onDoneSetingDz(message):
    logMessage(message)
    global evntStatus
    if not evntStatus.settingDz or evntStatus.settingDzAuthor != message.from_user.id:
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        bot.send_message(message.chat.id, 'Понял, принял, обработал')
        evntStatus.settingDz = False


@bot.callback_query_handler(func = lambda call: call.data == "/done")
def onDoneSetingDzCallback(call):
    logMessage(call, callback=True)
    global evntStatus
    if not evntStatus.settingDz or evntStatus.settingDzAuthor != call.from_user.id:
        bot.send_message(call.message.chat.id,f'{call.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        bot.send_message(call.message.chat.id, 'Понял, принял, обработал')
        evntStatus.settingDz = False
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


@bot.message_handler(content_types=['text','photo','audio'])
def onMessage(message):
    logMessage(message)
    if message.content_type == "text" and message.text[:1] == "/":
        bot.send_message(message.chat.id,"Команда не найдена: "+message.text)
    
    if evntStatus.settingDz and evntStatus.settingDzAuthor == message.from_user.id:
        d = Models.dz.Dz(evntStatus.settingDzDate, message.chat.id, message.message_id)
        d.push()


def main():
    dbacsessor.initDB()
    bot.polling(True)

if __name__ == "__main__":
    main()