import telebot
import re
import datetime
from telebot import types

import Models.dz
import dbacsessor
import Models.UI
import config as cfg
import MISC.events

bot = telebot.TeleBot(cfg.Token)

evntStatus = MISC.events.EventStatus()


def logMessage(message, callback=False):
    if callback:
        print(message.from_user.first_name, "@", message.from_user.id, "callback :", message.data)
    else:
        print(message.from_user.first_name,"@",message.from_user.id, message.content_type , ":", message.text)


@bot.message_handler(commands=['start', 'help'])
def startMessage(message):
    logMessage(message)
    if message.text == "/start":
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nЭтот бот поможет нам с дз)\nПреступим!')
    bot.send_message(message.chat.id, """
/help - Показывает это сообщение
/getDz - Возвращает дз на определенную дату
/setDz - Добавляет дз на определенную дату""")



@bot.message_handler(regexp="/getDz \d\d.\d\d.\d\d\d\d")
def onGetDz(message):
    logMessage(message)
    #Handling Exception, wich would be thrown gives us invalid date like 44.13.2014 
    try:
        for dz in Models.dz.getDz(message.text[7:]):
            dz.forward(bot, message.chat.id)
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /getDz (день.месяц.год)\nПример /getDz 01.11.2019")




@bot.callback_query_handler(func = lambda call: re.match("/getDz \d\d.\d\d.\d\d\d\d", call.data))
def onGetDzCallback(call):
    logMessage(call, callback=True)
    #I'm dont handling exeptions because user can't get acces to this method
    for dz in Models.dz.getDz(call.data[7:]): 
        dz.forward(bot, call.message.chat.id)
    

@bot.message_handler(commands=["getDz"])
def onGetDzWithOutDate(message):
    logMessage(message)
    Models.UI.getDz(bot, message.chat.id)

#=========================================================

@bot.message_handler(regexp="/setDz \d\d.\d\d.\d\d\d\d")
def onSetDz(message):
    logMessage(message)
    #Handling Exception, wich would be thrown gives us invalid date like 44.13.2014 
    try:
        Models.dz.validDate(message.text[7:])
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /setDz (день.месяц.год)\nПример /setDz 01.11.2019")
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
    bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text[7:12]}', reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzDate = message.text[7:]


@bot.message_handler(commands=["setDz"])
def onSetDzWithOutDate(message):
    logMessage(message)
    Models.UI.setDz(bot, message.chat.id)


@bot.callback_query_handler(func = lambda call: re.match("/setDz \d\d.\d\d.\d\d\d\d", call.data))
def onSetDzCallback(call):
    logMessage(call, callback=True)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
    bot.send_message(call.message.chat.id,f'{call.from_user.first_name}, Вы добавляете дз на {call.data[7:12]}', reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzDate = call.data[7:]


@bot.callback_query_handler(func=lambda call: call.data == "/setDzWithDate")
def onSetDzWithDateCallback(call):
    logMessage(call, callback=True)
    bot.send_message(call.message.chat.id, "Укажите дату\n(день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
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
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {datestr}', reply_markup=keyboard)

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, getDate)
    evntStatus.settingDz = True


@bot.message_handler(commands=['done'])
def onDoneSetingDz(message):
    logMessage(message)
    global evntStatus
    if not evntStatus.settingDz:
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        evntStatus.settingDz = False


@bot.callback_query_handler(func = lambda call: call.data == "/done")
def onDoneSetingDzCallback(call):
    logMessage(call, callback=True)
    global evntStatus
    if not evntStatus.settingDz:
        bot.send_message(call.message.chat.id,f'{call.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        evntStatus.settingDz = False


@bot.message_handler(content_types=['text','photo','audio'])
def onMessage(message):
    logMessage(message)
    if message.content_type == "text" and message.text[:1] == "/":
        bot.send_message(message.chat.id,"Команда не найдена: "+message.text)
    
    if evntStatus.settingDz:
        d = Models.dz.Dz(evntStatus.settingDzDate, message.chat.id, message.message_id)
        d.push()


def main():
    dbacsessor.initDB()
    bot.polling(True)

if __name__ == "__main__":
    main()