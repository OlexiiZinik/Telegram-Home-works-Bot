import telebot
import datetime
from telebot import types

import Models.dz


def mainMenuKeyboard():
    pass


def selectDateKeyboard(searchExisting=True):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    if searchExisting:
        for date in Models.dz.getExitstingDzDates():
            buttons.append(types.InlineKeyboardButton(date.strftime("%d.%m"), callback_data='/get_dz '+date.strftime("%d.%m.%Y")))
    else:
        date_list = []
        i = 1
        count = 0
        while count < 7:
            next_day = datetime.datetime.today() + datetime.timedelta(days=i)
            if next_day.strftime("%A") != "Sunday" and next_day.strftime("%A") != "Saturday":
                date_list.append(next_day)
                count += 1
            i += 1

        for date in date_list:
            buttons.append(types.InlineKeyboardButton(date.strftime("%d.%m"), callback_data='/set_dz '+date.strftime("%d.%m.%Y")))
        buttons.append(types.InlineKeyboardButton("Установить другую дату", callback_data='/setDzWithDate'))

    keyboard.add(*buttons)
    return keyboard


def getDz(bot, user):
    bot.send_message(user,"Выберете дату", reply_markup=selectDateKeyboard())


def setDz(bot, user):
    bot.send_message(user,"Выберете дату", reply_markup=selectDateKeyboard(searchExisting=False))