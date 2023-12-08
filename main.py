import telebot
import sqlite3

import search_movie as search
# import filter_movie as filter
import database_logic as data

from telebot import types
from kinopoisk_unofficial.kinopoisk_api_client import KinopoiskApiClient
from kinopoisk_unofficial.model.filter_country import FilterCountry
from kinopoisk_unofficial.model.filter_order import FilterOrder
from kinopoisk_unofficial.model.filter_genre import FilterGenre
from kinopoisk_unofficial.request.films.film_search_by_filters_request import FilmSearchByFiltersRequest


api_client = KinopoiskApiClient("4f159a5f-7bdd-47e5-ab5b-0ee99ecb2e3f")
bot = telebot.TeleBot('6891665743:AAE6qepTypG9luzTQwukw6tiNGwtzB1tJLM')


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect(f'database/client{message.chat.id}_info.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS films (id varchar(50), name varchar(50), year varchar(4))')
    conn.commit()
    cur.close()

    file = open(f"tmp_for_clients/{message.chat.id}.txt", "w")
    file.close()

    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    markup.add(search_btn, filter_btn, saves_btn, help_btn)
    text = ("Привет! 👋🎬 Я КиноБот. Если ты хочешь найти фильм, посмотреть список отложенных или узнать о схожих "
            "фильмах, я готов тебе помочь! Просто воспользуйся кнопками ниже. Наши возможности включают поиск "
            "фильмов, отбор фильмов по критериям, сохранение понравившихся фильмов, а также просмотр информации о "
            "текущих и отложенных фильмах. Если у тебя есть вопросы - спрашивай! 🔍🔗💾")
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def callback_worker(callback):
    if callback.data == "search":
        msg = bot.send_message(callback.message.chat.id, "Введите название фильма:")
        bot.register_next_step_handler(msg, search.search)
    elif callback.data == "filter":
        msg = bot.send_message(callback.message.chat.id, "Введите жанр фильма:")
        bot.register_next_step_handler(msg, process_genre_step)
    elif callback.data == "saves":
        msg = bot.send_message(callback.message.chat.id, "Отложенные фильмы:")
        data.show_movies_list(msg)
    elif callback.data == "save":
        msg = bot.send_message(callback.message.chat.id, "Добавлю фильм в отложенные")
        data.add_to_list(msg)
    elif callback.data == "same":
        msg = bot.send_message(callback.message.chat.id, "Сколько фильмов подобрать? (до 10)")
        bot.register_next_step_handler(msg, search.show_related)
    elif callback.data == "delete":
        msg = bot.send_message(callback.message.chat.id, "Введи ID фильма который вы хотите удалить из списка:")
        bot.register_next_step_handler(msg, data.delete_from_list)
    elif callback.data == "help":
        markup = types.InlineKeyboardMarkup(row_width=1)

        search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
        filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
        saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')

        rule_text = f"Привет! 👋 Я бот, который может помочь тебе найти или подобрать фильм:\n" \
                    f"🔍 Искать фильм по названию и выдавать краткие сведения.\n" \
                    f"🔍🔗 Найти фильмы по критериям.\n" \
                    f"💾 Добавить фильм в отложенные.\n"

        markup.add(search_btn, filter_btn, saves_btn)
        bot.send_message(callback.message.chat.id, rule_text, reply_markup=markup)



genre = None
from_year = 0
to_year = 0
rating = 0.0
country = None


def process_genre_step(message):
    global genre
    genre = str(message.text)
    text = """С какого по какой год искать? (1980-1990)
    разница между годами должна быть не меньше 1!"""
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, process_year_step)


def process_year_step(message):
    global from_year
    global to_year

    msg = str(message.text)
    try:
        time = msg.split("-")
        from_year = int(time[0])
        to_year = int(time[1])
        if from_year >= to_year:
            msg = bot.send_message(message.chat.id, "Первый год должен быть меньше второго!")
            bot.register_next_step_handler(msg, process_year_step)
        else:
            msg = bot.send_message(message.chat.id, "Минимальный рейтинг (от 1 до 10)?")
            bot.register_next_step_handler(msg, process_rating_step)
    except:
        msg = bot.send_message(message.chat.id, "Год должен быть числом от 1900 - 2023")
        bot.register_next_step_handler(msg, process_year_step)



def process_rating_step(message):
    global rating
    try:
        rating = float(message.text)
        msg = bot.send_message(message.chat.id, "Страна производства?")
        bot.register_next_step_handler(msg, process_country_step)
    except:
        msg = bot.send_message(message.chat.id, "Рейтинг должен быть числом от 1 до 10")
        bot.register_next_step_handler(msg, process_country_step)



def process_country_step(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')
    markup.add(search_btn, filter_btn, help_btn)

    global country
    global genre
    global from_year
    global to_year
    global rating
    country = message.text

    request = FilmSearchByFiltersRequest()
    request.year_from = from_year
    request.year_to = to_year
    request.rating_from = rating
    request.order = FilterOrder.RATING
    request.add_genre(FilterGenre(1, genre))
    # genre_list = genre.split(", ")
    # id_iter = 1
    # for genre_ in genre_list:
    #     request.add_genre(FilterGenre(id_iter, genre_))
    #     id_iter += 1

    request.add_country(FilterCountry(1, country))

    # Выполнить запрос с использованием фильтров и обрабатывать результаты, например:
    films = api_client.films.send_film_search_by_filters_request(request)
    film_info = ""
    if len(films.items) != 0:
        iter = 1
        for film in films.items[:5]:
            # форматирование информации о фильме
            film_info += f"#{iter} : {film.name_ru}\n" \
                         f"Год: {film.year}\n" \
                         f"Рейтинг: {film.rating_kinopoisk}\n" \
                         f"Постер фильма: {film.poster_url}\n\n"
            bot.send_message(message.chat.id, film_info)
            film_info = ""
            iter += 1

        film_info = f"Вот фильмы по вашему критерию из КиноПоиска"
        bot.send_message(message.chat.id, film_info, reply_markup=markup)
    else:
        film_info = f"Ой! Что то не так, попробуйте еще раз"
        bot.send_message(message.chat.id, film_info, reply_markup=markup)


bot.polling()
