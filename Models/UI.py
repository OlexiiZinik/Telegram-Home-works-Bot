import telebot
import datetime
from telebot import types

import Models.dz
from MISC.languages import LANGUAGES as LNGS


def mainMenuKeyboard():
    pass

# keyboard generator
def selectDateKeyboard(langCode, searchExisting=True):
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
        buttons.append(types.InlineKeyboardButton(LNGS[langCode]['Select other date'], callback_data='/setDzWithDate'))

    keyboard.add(*buttons)
    return keyboard


def getDz(bot, user, languageCode):
    bot.send_message(user, LNGS[languageCode]['Select date'], reply_markup=selectDateKeyboard(languageCode))


def setDz(bot, user, languageCode):
    bot.send_message(user, LNGS[languageCode]['Select date'], reply_markup=selectDateKeyboard(languageCode, searchExisting=False))