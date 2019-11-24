import telebot
from telebot import types

import Models.dz

def mainMenuKeyboard():
    pass


def selectDateKeyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for date in Models.dz.isExitstsDzAfter():
        buttons.append(types.InlineKeyboardButton(date, callback_data='/getDz '+date),)
    keyboard.add(*buttons)
    return keyboard


def getDz(bot, user):
     bot.send_message(user,"something", reply_markup=selectDateKeyboard())