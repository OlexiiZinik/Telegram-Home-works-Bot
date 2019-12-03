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
from  MISC.languages import LANGUAGES as LNGS

# Creating telebot object
bot = telebot.TeleBot(cfg.Token)

# Setting up logging mechanism
logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
ch = [logging.StreamHandler(sys.stdout),logging.FileHandler("bot.log", mode='a')]
logger.addHandler(ch[0])
logger.addHandler(ch[1])
logger.setLevel(logging.INFO)
ch[0].setFormatter(formatter)
ch[1].setFormatter(formatter)

# This thing explains to bot, what he is doing right now
evntStatus = MISC.events.EventStatus()

# Function that logging all messages & callbacks
def logMessage(message, callback=False):
    if callback:
       logger.log(logging.INFO, str(message.from_user.first_name) + " @ " + str(message.from_user.id) + " on " + str(message.message.chat.id) + " callback : " + message.data)
    else:
       logger.log(logging.INFO, str(message.from_user.first_name) + " @ " + str(message.from_user.id) + " on " + str(message.chat.id) + " " + message.content_type + " " + str(message.from_user.language_code) + " : " + message.text)

# start & help commands hendler
@bot.message_handler(commands=['start', 'help'])
def startMessage(message):
    logMessage(message)
    if message.text == "/start":
        # Answer is based on user language, by default it will use english
        # Yes, it's complicated but it works, like i said
        # Every where else when bot is send something to user it checks his language
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Welcome'].format(message.from_user.first_name))
    bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Help'])


# get_dz (date) command hendler. It uses regular expression to get date
@bot.message_handler(regexp="/get_dz \d\d.\d\d.\d\d\d\d")
def onGetDz(message):
    logMessage(message)
    #Handling Exception, wich would be thrown gives us invalid date like 44.13.2014 
    try:
        for dz in Models.dz.getDz(message.text[8:]):
            dz.forward(bot, message.chat.id)
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Invalid date'].format("get_dz"))



# get_dz (date) callback handler(it called when user press specific key on Telegram keyboard). It uses regular expression to get date
@bot.callback_query_handler(func = lambda call: re.match("/get_dz \d\d.\d\d.\d\d\d\d", call.data))
def onGetDzCallback(call):
    logMessage(call, callback=True)
    #I'm not handling exceptions because user can't get access to this method
    bot.send_message(call.message.chat.id, LNGS[call.from_user.language_code]['Ret HM'].format(call.data[8:13]))
    for dz in Models.dz.getDz(call.data[8:]): 
        dz.forward(bot, call.message.chat.id)
    
# get_dz command hendler.
@bot.message_handler(commands=["get_dz"])
def onGetDzWithOutDate(message):
    logMessage(message)
    Models.UI.getDz(bot, message.chat.id, message.from_user.language_code)

#=========================================================

# set_dz (date) command hendler. It uses regular expression to get date
@bot.message_handler(regexp="/set_dz \d\d.\d\d.\d\d\d\d")
def onSetDz(message):
    logMessage(message)
    # Handling Exception, which would be thrown, if user gives us invalid date like 44.13.2014 
    try:
        Models.dz.validDate(message.text[8:])
    except Models.dz.InvalidDateException:
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Invalid date'].format("set_dz"))
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(LNGS[message.from_user.language_code]['BUTTONS']['Done'], callback_data="/done"))
    bot.send_message(message.chat.id, LNGS[call.from_user.language_code]['Ready to read'].format(message.from_user.first_name, message.text[8:13]), reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzAuthor = message.from_user.id
    evntStatus.settingDzDate = message.text[8:]


# set_dz command hendler.
@bot.message_handler(commands=["set_dz"])
def onSetDzWithOutDate(message):
    logMessage(message)
    Models.UI.setDz(bot, message.chat.id, message.from_user.language_code)

# set_dz (date) callback handler(it called when user press specific key on Telegram keyboard). It uses regular expression to get date
@bot.callback_query_handler(func = lambda call: re.match("/set_dz \d\d.\d\d.\d\d\d\d", call.data))
def onSetDzCallback(call):
    logMessage(call, callback=True)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(LNGS[call.from_user.language_code]['BUTTONS']['Done'], callback_data="/done"))
    bot.edit_message_text(LNGS[call.from_user.language_code]['Ready to read'].format(call.from_user.first_name, call.data[8:13]), call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzAuthor = call.from_user.id
    evntStatus.settingDzDate = call.data[8:]


# callback which asks user specific date 
@bot.callback_query_handler(func=lambda call: call.data == "/setDzWithDate")
def onSetDzWithDateCallback(call):
    logMessage(call, callback=True)
    bot.edit_message_text(LNGS[call.from_user.language_code]['Get date'], call.message.chat.id, call.message.message_id, reply_markup=None)
    def getDate(message):
        logMessage(message)
        global evntStatus
        datestr = ""
        if re.match("\d\d.\d\d.\d\d\d\d", message.text):
            datestr = message.text
        elif re.match("\d\d.\d\d", message.text):
            datestr = message.text+"."+str(datetime.datetime.today().year)
        else:
            bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Get date fail'])
            bot.register_next_step_handler_by_chat_id(message.chat.id, getDate)
            return
        try:
            Models.dz.validDate(datestr)
        except Models.dz.InvalidDateException:
            bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Get date fail'])
            bot.register_next_step_handler_by_chat_id(message.chat.id, getDate)
            return
        #If anything goes wrong, we interrupt method, say user that he is an idiot and register next message handler, again ...
        #Else user can send home works
        evntStatus.settingDzDate = datestr
        evntStatus.settingDzAuthor = message.from_user.id
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(LNGS[message.from_user.language_code]['BUTTONS']['Done'], callback_data="/done"))
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Ready to read'].format(call.from_user.first_name, message.text), reply_markup=keyboard)

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, getDate)
    evntStatus.settingDz = True

# done command handler. It using to stop adding home works
@bot.message_handler(commands=['done'])
def onDoneSetingDz(message):
    logMessage(message)
    global evntStatus
    if not evntStatus.settingDz or evntStatus.settingDzAuthor != message.from_user.id:
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Done fail'].format(message.from_user.first_name))
    else:
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Done success'])
        evntStatus.settingDz = False

# done callback handler(it called when user press specific key on Telegram keyboard). It using to stop adding home works
@bot.callback_query_handler(func = lambda call: call.data == "/done")
def onDoneSetingDzCallback(call):
    logMessage(call, callback=True)
    global evntStatus
    if not evntStatus.settingDz or evntStatus.settingDzAuthor != call.from_user.id:
        bot.send_message(call.message.chat.id, LNGS[call.from_user.language_code]['Done fail'].format(call.from_user.first_name))
    else:
        bot.send_message(call.message.chat.id, LNGS[call.from_user.language_code]['Done success'])
        evntStatus.settingDz = False
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# default message handler
@bot.message_handler(content_types=['text','photo','audio'])
def onMessage(message):
    logMessage(message)
    if message.content_type == "text" and message.text[:1] == "/":
        bot.send_message(message.chat.id, LNGS[message.from_user.language_code]['Command not found'].format(message.text))
    # if user adding home works we push them into database
    if evntStatus.settingDz and evntStatus.settingDzAuthor == message.from_user.id:
        d = Models.dz.Dz(evntStatus.settingDzDate, message.chat.id, message.message_id)
        d.push()


def main():
    # Initialising database just in case it was not exist
    dbacsessor.initDB()
    bot.polling(True)

if __name__ == "__main__":
    main()