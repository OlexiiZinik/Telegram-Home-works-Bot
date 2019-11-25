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

"""
{
    'content_type': 'text',
    'message_id': 43,
    'from_user': {
        'id': 394077335,
        'is_bot': False,
        'first_name': 'Ольошик',
        'username': 'Vyxyxol',
        'last_name': None,
        'language_code': 'ru'
        },
    'date': 1573326941,
    'chat': {
        'type': 'private',
        'last_name': None,
        'first_name': 'Ольошик',
        'username': 'Vyxyxol',
        'id': 394077335,
        'title': None,
        'all_members_are_administrators': None,
        'photo': None,
        'description': None,
        'invite_link': None,
        'pinned_message': None,
        'sticker_set_name': None,
        'can_set_sticker_set': None
    },
    'forward_from_chat': None,
    'forward_from': None,
    'forward_date': None,
    'reply_to_message': None,
    'edit_date': None,
    'media_group_id': None,
    'author_signature': None,
    'text': 's',
    'entities': None,
    'caption_entities': None,
    'audio': None,
    'document': None,
    'photo': None,
    'sticker': None,
    'video': None,
    'video_note': None,
    'voice': None,
    'caption': None,
    'contact': None,
    'location': None,
    'venue': None,
    'new_chat_member': None,
    'new_chat_members': None,
    'left_chat_member': None,
    'new_chat_title': None,
    'new_chat_photo': None,
    'delete_chat_photo': None,
    'group_chat_created': None,
    'supergroup_chat_created': None,
    'channel_chat_created': None,
    'migrate_to_chat_id': None,
    'migrate_from_chat_id': None,
    'pinned_message': None,
    'invoice': None,
    'successful_payment': None,
    'connected_website': None,
    'json': {'message_id': 43, 'from': {'id': 394077335, 'is_bot': False, 'first_name': 'Ольошик', 'username': 'Vyxyxol', 'language_code': 'ru'}, 'chat': {'id': 394077335, 'first_name': 'Ольошик', 'username': 'Vyxyxol', 'type': 'private'}, 'date': 1573326941, 'text': 's'}}
"""
def logMessage(message):
    print(message.from_user.first_name,"@",message.from_user.id, message.content_type , ":", message.text)


@bot.message_handler(commands=['start', 'help'])
def startMessage(message):
    logMessage(message)
    print(message.from_user.first_name,"@",message.from_user.id,":", message.text)
    if message.text == "/start":
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nЭтот бот поможет нам с дз)\nПреступим!')
    bot.send_message(message.chat.id, """
/help - Показывает это сообщение
/getDz <дата> - Возвращает дз на определенную дату. Пример /getDz 01.01.1978
/setDz <дата> - Добавляет дз на определенную дату. Пример /getDz 01.01.1978""")



@bot.message_handler(regexp="/getDz \d\d.\d\d.\d\d\d\d")
def onGetDz(message):
    logMessage(message)
    try:
        d = datetime.datetime.strptime(message.text[7:], "%d.%m.%Y")
        for dz in Models.dz.getDz(message.text[7:]):
            bot.forward_message(message.chat.id, dz[1], dz[2])
    except Exception as e:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /getDz (день.месяц.год)\nПример /getDz 01.11.2019")




@bot.callback_query_handler(func = lambda call: re.match("/getDz \d\d.\d\d.\d\d\d\d", call.data))
def onGetDzCallback(call):
    msg = call.message
    msg.text = call.data
    logMessage(msg)
    for dz in Models.dz.getDz(call.data[7:]):
        bot.forward_message(call.message.chat.id, dz[1], dz[2])
    

@bot.message_handler(commands=["getDz"])
def onGetDzWithOutDate(message):
    logMessage(message)
    Models.UI.getDz(bot, message.chat.id)

#=========================================================

@bot.message_handler(regexp="/setDz \d\d.\d\d.\d\d\d\d")
def onSetDz(message):
    logMessage(message)
    try:
        d = datetime.datetime.strptime(message.text[7:], "%d.%m.%Y")
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text[7:12]}', reply_markup=keyboard)
        global evntStatus
        evntStatus.settingDz = True
        evntStatus.settingDzDate = message.text[7:]
    except Exception as e:
        bot.send_message(message.chat.id, "Не правельно!\nукажите /setDz (день.месяц.год)\nПример /setDz 01.11.2019")


@bot.message_handler(commands=["setDz"])
def onSetDzWithOutDate(message):
    logMessage(message)
    Models.UI.setDz(bot, message.chat.id)


@bot.callback_query_handler(func = lambda call: re.match("/setDz \d\d.\d\d.\d\d\d\d", call.data))
def onSetDzCallback(call):
    msg = call.message
    msg.text = call.data
    logMessage(msg)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
    bot.send_message(call.message.chat.id,f'{call.from_user.first_name}, Вы добавляете дз на {call.data[7:12]}', reply_markup=keyboard)
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzDate = call.data[7:]


@bot.callback_query_handler(func=lambda call: call.data == "/setDzWithDate")
def onSetDzWithDate(call):
    msg = call.message
    msg.text = call.data
    logMessage(msg)
    bot.send_message(call.message.chat.id, "Укажите дату\n(день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
    def getDate(message): 
        if re.match("\d\d.\d\d.\d\d\d\d", message.text):
            try:
                d = datetime.datetime.strptime(message.text, "%d.%m.%Y")
                global evntStatus
                evntStatus.settingDzDate = message.text
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
                bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text}', reply_markup=keyboard)
                return
            except Exception as e:
                pass
        elif re.match("\d\d.\d\d", message.text):
            try:
                date = datetime.datetime.strptime(message.text+"."+str(datetime.datetime.today().year), "%d.%m.%Y")
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton("Готово", callback_data="/done"))
                bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text[7:12]}', reply_markup=keyboard)
                evntStatus.settingDzDate = datetime.datetime.strftime(date,"%d.%m.%Y")
                return
            except Exception as e:
                pass
        
        bot.send_message(message.chat.id, "Не правельно!\nукажите (день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019")
        bot.register_next_step_handler_by_chat_id(message.chat.id, getDate)

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
    msg = call.message
    msg.text = call.data
    logMessage(msg)
    global evntStatus
    if not evntStatus.settingDz:
        bot.send_message(call.message.chat.id,f'{call.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        evntStatus.settingDz = False


@bot.message_handler(content_types=['text','photo','audio'])
def onMessage(message):
    logMessage(message)
    #print(message)
    if message.content_type == "text" and message.text[:1] == "/":
        bot.send_message(message.chat.id,"Команда не найдена: "+message.text)
    
    if evntStatus.settingDz:
        d = Models.dz.Dz(evntStatus.settingDzDate, message.chat.id, message.message_id)
        d.push()
        #dba.setDz(settingDzDate, message.chat.id, message.message_id)


def main():
    dbacsessor.initDB()
    #dba.setDz("12.12.3333", "ukrmova", "12345678", "12313547578", "12")
    bot.polling(True)

if __name__ == "__main__":
    main()