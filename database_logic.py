import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot('6891665743:AAE6qepTypG9luzTQwukw6tiNGwtzB1tJLM')


def add_to_list(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    conn = sqlite3.connect(f'database/client{message.chat.id}_info.sql')
    cur = conn.cursor()

    with open(f"tmp_for_clients/{message.chat.id}.txt", "r") as file:
        line = file.readline().strip()

    id, name, year = line.split("|")

    cur.execute("INSERT INTO films (id, name, year) VALUES ('%s', '%s', '%s')" % (id, name, year))

    conn.commit()
    cur.close()
    conn.close()

    markup.add(search_btn, filter_btn, saves_btn, help_btn)
    bot.send_message(message.chat.id, "Фильм сохранен!", reply_markup=markup)


def delete_from_list(message):
    id = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    conn = sqlite3.connect(f'database/client{message.chat.id}_info.sql')
    cur = conn.cursor()

    cur.execute("DELETE FROM films WHERE id = '%s'" % (id))

    conn.commit()
    cur.close()
    conn.close()

    markup.add(search_btn, filter_btn, saves_btn, help_btn)
    bot.send_message(message.chat.id, "Фильм убран!", reply_markup=markup)


def show_movies_list(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    delete_btn = types.InlineKeyboardButton("🗑️ Убрать фильм из списка", callback_data='delete')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    conn = sqlite3.connect(f'database/client{message.chat.id}_info.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM films')
    films = cur.fetchall()

    info = ""
    if films:
        iter = 1
        for elem in films:
            info += f"#{iter}: ID: {elem[0]} |  Название: {elem[1]}  |  Год: {elem[2]}\n"
            iter += 1

    else:
        info = "пусто!"

    cur.close()
    conn.close()

    markup.add(search_btn, filter_btn, delete_btn, help_btn)
    bot.send_message(message.chat.id, info, reply_markup=markup)
