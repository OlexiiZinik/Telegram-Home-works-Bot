import telebot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import Models.dz
import dbacsessor
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
    bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы запросили дз на {message.text[7:]}')
    
    for dz in Models.dz.getDz(message.text[7:]):
        bot.forward_message(message.chat.id, dz[1], dz[2])
        #bot.send_message(message.chat.id, f'{dz}')


@bot.message_handler(commands=['done'])
def onDoneSetingDz(message):
    logMessage(message)
    global evntStatus
    if not evntStatus.settingDz:
        bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы не давали коанды на добавление домашнего задания!')
    else:
        evntStatus.settingDz = False

@bot.message_handler(regexp="/setDz \d\d.\d\d.\d\d\d\d")
def onSetDz(message):
    logMessage(message)
    bot.send_message(message.chat.id,f'{message.from_user.first_name}, Вы добавляете дз на {message.text[7:]}.\nИспользуйте /done чтобы завершить')
    global evntStatus
    evntStatus.settingDz = True
    evntStatus.settingDzDate = message.text[7:]



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