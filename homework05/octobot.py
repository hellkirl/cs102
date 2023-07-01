import json
import re
from datetime import datetime, timedelta
from os.path import exists

import dateutil  # type: ignore
import gspread  # type: ignore
import pandas as pd  # type: ignore
import requests  # type: ignore
import telebot  # type: ignore
from dateutil.parser import parse  # type: ignore

bot = telebot.TeleBot("")


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
    regex = r"^(https?://|www\.)\S*\.ru$"
    if re.match(regex, url):
        return True
    regex = r"^\S*\.ru$"
    if re.match(regex, url):
        return True
    regex = r"^en\S*\.[a-z]+\.[a-z]{2,3}$"
    if re.match(regex, url):
        return False

    return False


def convert_date(date: str = "01/01/00"):
    """Конвертируем дату из строки в datetime"""
    return datetime.strptime(date, "%d/%m/%y")


def connect_table(message):
    """Подключаемся к Google-таблице"""
    url = message.text
    sheet_id = ""
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
    all_messages(message)


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
        info = bot.send_message(message.chat.id, "Отправьте ссылку на вашу Google-таблицу")
        bot.register_next_step_handler(info, check_rights)
    elif message.text == "Редактировать предметы":
        edit_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        edit_markup.row("Добавить предмет")
        edit_markup.row("Изменить предмет")
        edit_markup.row("Удалить предмет")
        edit_markup.row("Удалить всё")
        edit_markup.row("Вернуться назад")
        info = bot.send_message(message.chat.id, "Выберите дальнейшее действие", reply_markup=edit_markup)
        bot.register_next_step_handler(info, choose_subject_action)
    elif message.text == "Редактировать дедлайны":
        worksheet, u, df = access_current_sheet()
        if not worksheet.col_values(1)[1:]:
            bot.send_message(message.chat.id, "В таблице ничего нет")
            all_messages(message)
        else:
            deadline_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            deadline_markup.row("Добавить дедлайн")
            deadline_markup.row("Изменить дедлайн")
            deadline_markup.row("Вернуться назад")
            info = bot.send_message(message.chat.id, "Что изменить в дедлайнах?", reply_markup=deadline_markup)
            bot.register_next_step_handler(info, choose_deadline_action)
    elif message.text == "Посмотреть дедлайны на этой неделе":
        worksheet, u, df = access_current_sheet()
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        deadlines = []

        for row in worksheet.get_all_values()[1:]:
            name = row[0]
            dates = []
            for date_str in row[2:]:
                if is_valid_date(date_str):
                    deadline = datetime.strptime(date_str, "%d/%m/%y").date()
                    if today <= deadline < week_end:
                        dates.append(deadline.strftime("%d.%m.%y"))
            if dates:
                deadlines.append(f"{name}: " + ", ".join(dates))

        if not deadlines:
            response = "Нет дедлайнов на ближайшую неделю"
        else:
            response = "Дедлайны на этой неделе:\n" + "\n".join(deadlines)

        bot.send_message(message.chat.id, response)
        all_messages(message)


def choose_subject_action(message):
    """Выбираем действие в разделе Редактировать предметы"""
    worksheet, u, df = access_current_sheet()
    if message.text == "Добавить предмет":
        info = bot.send_message(message.chat.id, "Введите название предмета")
        new_row = df.shape[0] + 2
        bot.register_next_step_handler(info, add_new_subject, new_row)
    elif message.text == "Изменить предмет":
        reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for subject in worksheet.col_values(1)[1:]:
            reply.row(f"{subject}")
        info = bot.send_message(message.chat.id, "Выберите предмет", reply_markup=reply)
        bot.register_next_step_handler(info, update_subject)
    if message.text == "Удалить предмет":
        delete_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        subjects = len(worksheet.col_values(1)) + 1
        for _ in range(2, subjects):
            delete_markup.row(worksheet.cell(_, 1).value)
        info = bot.send_message(message.chat.id, "Какой предмет надо удалить?", reply_markup=delete_markup)
        bot.register_next_step_handler(info, delete_subject)
    elif message.text == "Удалить всё":
        delete_all_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        delete_all_markup.row("Да, точно")
        delete_all_markup.row("Нет")
        info = bot.send_message(message.chat.id, "Вы точно хотите удалить все?", reply_markup=delete_all_markup)
        bot.register_next_step_handler(info, choose_removal_option)
    elif message.text == "Вернуться назад":
        all_messages(message)


def choose_deadline_action(message):
    """Выбираем действие в разделе Редактировать дедлайн"""
    worksheet, u, df = access_current_sheet()
    if message.text == "Добавить дедлайн":
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        deadlines = len(worksheet.col_values(1)) + 1
        for i in range(2, deadlines):
            start_markup.row(worksheet.cell(i, 1).value)
        info = bot.send_message(
            message.chat.id, "Для какого предмета хотите добавить дедлайн?", reply_markup=start_markup
        )
        bot.register_next_step_handler(info, choose_subject)
    elif message.text == "Изменить дедлайн":
        start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        deadlines = len(worksheet.col_values(1)) + 1
        for i in range(2, deadlines):
            start_markup.row(worksheet.cell(i, 1).value)
        info = bot.send_message(
            message.chat.id, "Для какого предмета хотите поменять дедлайн?", reply_markup=start_markup
        )
        bot.register_next_step_handler(info, choose_subject)
    elif message.text == "Вернуться назад":
        all_messages(message)


def choose_removal_option(message):
    """Уточняем, точно ли надо удалить все"""
    if message.text == "Да":
        clear_subject_list(message)
    elif message.text == "Нет":
        all_messages(message)
    elif message.text == "Вернуться назад":
        all_messages(message)


def add_new_deadline(message):
    subject = message.text
    worksheet, u, df = access_current_sheet()
    cell = worksheet.find(subject)
    row = cell.row
    num_cols = len(worksheet.row_values(1))
    deadline_col = None
    for col in range(num_cols, 0, -1):
        if worksheet.cell(row, col).value:
            deadline_col = col
            break
    if deadline_col is None:
        deadline_col = num_cols + 1
    info = bot.send_message(message.chat.id, "Введите дату дедлайна")
    bot.register_next_step_handler(info, update_subject_deadline, subject, deadline_col)


def choose_subject(message):
    """Выбираем предмет, у которого надо отредактировать дедлайн"""
    info = bot.send_message(message.chat.id, "Введите номер работы")
    bot.register_next_step_handler(info, choose_task, message.text)


def choose_task(message, subject):
    """Выбираем конкретную работу, у которой надо отредактировать дедлайн"""
    info = bot.send_message(message.chat.id, "Введите новую дату дедлайна?")
    bot.register_next_step_handler(info, update_subject_deadline, subject, message.text)


def update_subject_deadline(message, subject, task):
    """Обновляем дедлайн"""
    worksheet, u, df = access_current_sheet()
    cell = worksheet.find(subject)
    column = int(task) + 2
    worksheet.update_cell(1, column, task)
    try:
        date = parse(message.text, dayfirst=True)
        today = datetime.now()
        if date > today + timedelta(days=365):
            info = bot.send_message(
                message.chat.id, "Дедлайн не должен быть больше, чем через год \nВведите другую дату дедлайна"
            )
            bot.register_next_step_handler(info, update_subject_deadline, subject, task)
            return
        elif date > today:
            worksheet.update_cell(cell.row, column, date.strftime("%d/%m/%y"))
            bot.send_message(message.chat.id, "Сделано!")
            all_messages(message)
        elif today - timedelta(days=1) < date < today + timedelta(days=1):
            worksheet.update_cell(cell.row, column, date.strftime("%d/%m/%y"))
            info = bot.send_message(message.chat.id, "Дедлайн добавлен")
            all_messages(message)
        else:
            info = bot.send_message(message.chat.id, "Дедлайн уже прошел", "Попробуйте ввести более позднюю дату")
            bot.register_next_step_handler(info, update_subject_deadline, subject, task)
            return
    except Exception:
        info = bot.send_message(message.chat.id, "Такой даты некорректна\nВведите другую дату")
        bot.register_next_step_handler(info, update_subject_deadline, subject, task)
        return


def add_new_subject(message, row):
    """Вносим новое название предмета в Google-таблицу"""
    worksheet, u, df = access_current_sheet()
    title = message.text
    if worksheet.find(title) is not None:
        info = bot.send_message(message.chat.id, "Такой предмет уже есть в таблице\nВведите другое название")
        bot.register_next_step_handler(info, add_new_subject, row)
        return
    else:
        worksheet.append_row(["предмет", "ссылка"])
        worksheet.update_cell(row, 1, message.text)
        info = bot.send_message(
            message.chat.id, "Если ссылки нет, то введите '-'. \nЕсли ссылка есть, то введите ссылку на этот предмет"
        )
        bot.register_next_step_handler(info, add_new_subject_url, row)


def add_new_subject_url(message, row):
    """Вносим новую ссылку на таблицу предмета в Google-таблицу"""
    url = message.text
    if url == "-":
        worksheet, u, df = access_current_sheet()
        worksheet.update_cell(row, 2, url)
        bot.send_message(message.chat.id, "Все получилось")
        all_messages(message)
    else:
        try:
            r = requests.get(url)
            if r.ok:
                worksheet, u, df = access_current_sheet()
                worksheet.update_cell(row, 2, url)
                bot.send_message(message.chat.id, "Все получилось")
                all_messages(message)
            else:
                info = bot.send_message(message.chat.id, "Некорректная ссылка. Отправьте другую")
                bot.register_next_step_handler(info, add_new_subject_url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError) as e:
            info = bot.send_message(message.chat.id, "Некорректная ссылка. Отправьте другую")
            bot.register_next_step_handler(info, add_new_subject_url, row)


def update_subject(message):
    """Обновляем информацию о предмете в Google-таблице"""
    worksheet, u, df = access_current_sheet()
    cell = worksheet.find(message.text)
    if cell:
        info = bot.send_message(message.chat.id, "Введите новое название предмета")
        bot.register_next_step_handler(info, add_new_subject, cell.row)
    else:
        info = bot.send_message(message.chat.id, "Такого предмета нет. Попробуйте еще раз")
        bot.register_next_step_handler(info, update_subject)
        return


def delete_subject(message):
    """Удаляем предмет в Google-таблице"""
    worksheet, u, df = access_current_sheet()
    cell = worksheet.find(message.text)
    if cell:
        worksheet.delete_rows(cell.row)
        bot.send_message(message.chat.id, "Предмет удален")
        all_messages(message)
    else:
        info = bot.send_message(message.chat.id, "Такого предмета нет. Попробуйте еще раз")
        bot.register_next_step_handler(info, delete_subject)


def clear_subject_list(message):
    """Удаляем все из Google-таблицы"""
    worksheet, u, df = access_current_sheet()
    worksheet.clear()
    bot.send_message(message.chat.id, "Всё удалено")
    all_messages(message)


def check_rights(message):
    try:
        if requests.get(message.text):
            start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            start_markup.row("Да")
            start_markup.row("Нет")
            start_markup.row("Вернуться назад...")
            info = bot.send_message(message.chat.id, "Вы предоставили мне доступ к таблице", reply_markup=start_markup)
            bot.register_next_step_handler(info, choose_rights_option)
    except Exception:
        info = bot.send_message(message.chat.id, "Ссылка некорректна")
        start(message)


def choose_rights_option(message):
    if message.text == "Да":
        connect_table(message)
    elif message.text == "Нет":
        info = bot.send_message(message.chat.id, "Сначала предоставьте права доступа")
        start(message)
    elif message.text == "Вернуться назад...":
        start(message)


@bot.message_handler(commands=["start"])
def start(message):
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if not exists("chat_id.txt"):
        with open("chat_id.txt", "w") as f:
            f.write(str(message.chat.id))
    if exists("tables.json"):
        start_markup.row("Подключить Google-таблицу")
    info = bot.send_message(
        message.chat.id,
        "Привет! Я бот, который будет помогать тебе следить за дедлайнами.",
        reply_markup=start_markup,
    )
    bot.register_next_step_handler(info, choose_action)


@bot.message_handler(func=lambda message: True)
def all_messages(message):
    all_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    all_markup.row("Посмотреть дедлайны на этой неделе")
    all_markup.row("Редактировать дедлайны")
    all_markup.row("Редактировать предметы")
    info = bot.send_message(message.chat.id, "Выберите дальнейшее действие", reply_markup=all_markup)
    bot.register_next_step_handler(info, choose_action)


if __name__ == "__main__":
    bot.infinity_polling()
