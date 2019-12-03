from collections import defaultdict

# In future {} will be replaced by USERNAME or something else
_phrases = {
    "ru" : {
        "Welcome"            : "Привет, {}!\nЭтот бот поможет нам с дз)\nПреступим!",
        "Help"               : "/help - Показывает это сообщение\n/get_dz - Возвращает дз на определенную дату\n/set_dz - Добавляет дз на определенную дату",
        "Invalid date"       : "Не правельно!\nукажите /{} (день.месяц.год)\nПример /{} 01.11.2019",
        "Ret HM"             : "Дз на {}",
        "Ready to read"      : "{}, вы добавляете дз на {}",
        "Get date"           : "Укажите дату\n(день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019",
        "Get date fail"      : "Не правельно!\nукажите (день.месяц) или (день.месяц.год)\nПример 01.11 или 01.11.2019",
        "Done fail"          : "{}, вы не давали коанды на добавление домашнего задания!",
        "Done success"       : "Понял, принял, обработал",
        "Command not found"  : "Команда не найдена: {}",
        "Select date"        : "Выберете дату",
        "Select other date"  : "Установить другую дату",

        "BUTTONS" : {
            "Done" : "Готово"
        }
    },
    "en" : {
        "Welcome"            : "Hi, {}!\nThis bot will help us with homework)\nLet's get started!",
        "Help"               : "/help - Displays this message\n/get_dz - Returns HM for a specific date\n/set_dz - Adds HM for a specific date",
        "Invalid date"       : "Wrong!\nSpecify /{} (day.month.year)\nExample /{} 01/01/2019",
        "Ret HM"             : "Homework on{}",
        "Ready to read"      : "{}, you are adding homework on {}",
        "Get date"           : "Specify (day.month.year) or (day.month)\nExample 01.11.2019 or 01.11",
        "Get date fail"      : "Wrong!\nSpecify (day.month.year) or (day.month)\nExample 01.11.2019 or 01.11",
        "Done fail"          : "{}, you did not give tasks to add homework!",
        "Done success"       : "Understood, accepted, processed",
        "Command not found"  : "Command not found: {}",
        "Select date"        : "Choose a date",
        "Select other date"  : "Set a different date",

        "BUTTONS" : {
            "Done" : "Done"
        }
    }
}

# If language code unknown, it will return english words 
LANGUAGES = defaultdict(lambda: _phrases['en'], _phrases)
# If language code is ua, it will return russian words
LANGUAGES['ua'] = _phrases['ru']