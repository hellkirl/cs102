import telebot
import gspread
import json
import pandas as pd
import re
from datetime import datetime, timedelta
from tabulate import tabulate

bot = telebot.TeleBot("6250275759:AAHTme7QlqaSJwOhHdYUxZNIaQXn4DsqjM8")


def is_valid_date(date: str = "01/01/00", divider: str = "/") -> bool:
    """Проверяем, что дата дедлайна валидна:
    - дата не может быть до текущей
    - не может быть позже, чем через год
    - не может быть такой, которой нет в календаре
    - может быть сегодняшним числом
    - пользователь не должен быть обязан вводить конкретный формат даты
    (например, только через точку или только через слеш)
    """
    if divider not in date or date.count(divider) != 2:
        return False

    date = date.replace(divider, "/")
    try:
        input_date = convert_date(date).date()
    except ValueError:
        return False

    current_date = datetime.today().date()
    future_date = current_date.replace(year=current_date.year + 1)

    return current_date <= input_date <= future_date


def is_valid_url(url: str = "") -> bool:
    """Проверяем, что ссылка рабочая"""
    regex = r"^(https?://)?(www\.)?([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}$"
    return re.match(regex, url) is not None


def convert_date(date: str = "01/01/00"):
    """Конвертируем дату из строки в datetime"""
    return datetime.strptime(date, "%d/%m/%y")


def connect_table(message):
    """Подключаемся к Google-таблице"""
    url = message.text
    sheet_id = "1TkvBrji118uBlewa8coYLCJS8RHbxgs5fpICLVT86tI"
    try:
        with open("tables.json") as json_file:
            tables = json.load(json_file)
        title = len(tables) + 1
        tables[title] = {"url": url, "id": sheet_id}
    except FileNotFoundError:
        tables = {0: {"url": url, "id": sheet_id}}
    with open("tables.json", "w") as json_file:
        json.dump(tables, json_file)
    bot.send_message(message.chat.id, "Таблица успешно подключена! ✅")


def access_current_sheet():
    """Обращаемся к Google-таблице"""
    with open("tables.json") as json_file:
        tables = json.load(json_file)
    sheet_id = tables[max(tables)]["id"]
    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1
    # Преобразуем Google-таблицу в таблицу pandas
    rows = worksheet.get_all_records()
    df = pd.DataFrame(rows)
    return worksheet, tables[max(tables)]["url"], df


def choose_action(message):
    """Обрабатываем действия верхнего уровня"""
    if message.text == "Подключить Google-таблицу":
        connect_table(message)
        bot.send_message(message.chat.id, "Для перехода в главное меню напиши 'дедлайн'")
    elif message.text == "Редактировать предметы":
        edit_subject(message)
    elif message.text == "Редактировать дедлайн":
        edit_deadline(message)
    elif message.text == "Посмотреть дедлайны на этой неделе":
        bot.send_message(message.chat.id, tabulate(access_current_sheet()[2], tablefmt="psql", showindex=False))


def choose_subject_action(message):
    """Выбираем действие в разделе Редактировать предметы"""
    if message.text == "Обновить информацию о предмете":
        update_subject(message)
    elif message.text == "Добавить новый предмет":
        msg = "Введите информацию о предмете в формате название/ссылка/дата выдачи/дедлайн"
    elif message.text == "Вернуться назад":
        ...


def choose_deadline_action(message):
    """Выбираем действие в разделе Редактировать дедлайн"""
    # PUT YOUR CODE HERE
    pass


def choose_removal_option(message):
    """Уточняем, точно ли надо удалить все"""
    # PUT YOUR CODE HERE
    pass


def choose_subject(message):
    """Выбираем предмет, у которого надо отредактировать дедлайн"""
    # PUT YOUR CODE HERE
    pass


def update_subject_deadline(message):
    """Обновляем дедлайн"""
    # PUT YOUR CODE HERE
    pass


def add_new_subject(message):
    """Вносим новое название предмета в Google-таблицу"""
    # PUT YOUR CODE HERE
    pass


def add_new_subject_url(message):
    """Вносим новую ссылку на таблицу предмета в Google-таблицу"""
    # PUT YOUR CODE HERE
    pass


def update_subject(message):
    """Обновляем информацию о предмете в Google-таблице"""
    # PUT YOUR CODE HERE
    pass


def delete_subject(message):
    """Удаляем предмет в Google-таблице"""
    # PUT YOUR CODE HERE
    pass


def clear_subject_list(message):
    """Удаляем все из Google-таблицы"""
    # PUT YOUR CODE HERE
    pass


@bot.message_handler(commands=["start"])
def start(message):
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_markup.row("Подключить Google-таблицу")
    info = bot.send_message(message.chat.id, "Подключим таблицу?", reply_markup=start_markup)
    bot.register_next_step_handler(info, choose_action)


@bot.message_handler(func=lambda message: True)
def all_messages(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row("Посмотреть дедлайны на этой неделе")
    markup.row("Редактировать дедлайн")
    markup.row("Редактировать предметы")
    info = bot.send_message(message.chat.id, "Что хотите сделать?", reply_markup=markup)
    bot.register_next_step_handler(info, choose_action)


@bot.message_handler(func=lambda message: message == "Редактировать предметы")
def edit_subject(message):
    edit_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    edit_markup.row("Обновить информацию о предмете")
    edit_markup.row("Добавить новый предмет")
    edit_markup.row("Добавить новую ссылку")
    edit_markup.row("Удалить предмет")
    edit_markup.row("Очистить таблицу с дедлайнами")
    edit_markup.row("Вернуться назад")
    info = bot.send_message(message.chat.id, "Как Вы хотите отредактировать предметы?", reply_markup=edit_markup)
    bot.register_next_step_handler(info, choose_subject_action)


@bot.message_handler(func=lambda message: message == "Редактировать дедлайн")
def edit_deadline(message):
    deadline_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    deadline_markup.row("Обновить дедлайн")
    deadline_markup.row("Удалить дедлайн")
    info = bot.send_message(
        message.chat.id, "Как Вы хотите отредактировать дедлайны?", reply_markup=deadline_markup
    )
    bot.register_next_step_handler(info, choose_deadline_action, callback=all_messages)


bot.infinity_polling()
