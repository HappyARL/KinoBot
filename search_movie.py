import telebot
import requests

from telebot import types
from kinopoisk_unofficial.kinopoisk_api_client import KinopoiskApiClient
from kinopoisk_unofficial.request.films.related_film_request import RelatedFilmRequest
from kinopoisk_unofficial.request.films.search_by_keyword_request import SearchByKeywordRequest


api_client = KinopoiskApiClient("4f159a5f-7bdd-47e5-ab5b-0ee99ecb2e3f")
bot = telebot.TeleBot('6891665743:AAE6qepTypG9luzTQwukw6tiNGwtzB1tJLM')

curr_film_year = 0
curr_film_name = None
curr_film_id = 0

def search(message):
    global curr_film_year
    global curr_film_name
    global curr_film_id

    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    related_btn = types.InlineKeyboardButton("🔗 Схожие фильмы", callback_data='same')
    save_btn = types.InlineKeyboardButton("💾 Добавить в отложенные", callback_data='save')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    film_title = message.text
    request = SearchByKeywordRequest(film_title)
    film = api_client.films.send_search_by_keyword_request(request)

    if len(film.films) != 0:
        curr_film = film.films[0]
        curr_genre = curr_film.genres[0].genre
        curr_country = curr_film.countries[0].country
        curr_cover = curr_film.poster_url

        film_info = f"🎬 Название: {curr_film.name_ru}\n" \
                    f"📅 Год: {curr_film.year}\n" \
                    f"🌍 Страна: {curr_country}\n" \
                    f"🎭 Жанр: {curr_genre}\n" \
                    f"⭐ Оценка: {curr_film.rating}\n\n" \
                    f"🔍 Краткое описание: \n{curr_film.description}\n" \
                    f"📷 {curr_cover}"

        curr_film_year = curr_film.year
        curr_film_name = curr_film.name_ru
        curr_film_id = curr_film.film_id

        file = open(f"tmp_for_clients/{message.chat.id}.txt", "w")
        file.write(f"{curr_film_id}|{curr_film_name}|{curr_film_year}")
        file.close()

        markup.add(search_btn, related_btn, save_btn, filter_btn, saves_btn, help_btn)
        bot.send_message(message.chat.id, film_info, reply_markup=markup)
    else:
        markup.add(related_btn, filter_btn, saves_btn, save_btn, help_btn)
        bot.send_message(message.chat.id, "Фильм не найден :(", reply_markup=markup)


def show_related(message):
    count = int(message.text)
    markup = types.InlineKeyboardMarkup(row_width=1)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    saves_btn = types.InlineKeyboardButton("💿 Отложенные", callback_data='saves')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')

    global curr_film_id
    global curr_film_name
    request = RelatedFilmRequest(curr_film_id)
    films = api_client.films.send_related_film_request(request)
    film_info = ""
    iter = 1

    for film in films.items[:count]:
        # форматирование информации о фильме
        film_info += f"#{iter} : {film.name_ru}\n" \
                     f"ID фильма: {film.film_id}\n" \
                     f"Постер фильма: {film.poster_url_preview}\n\n"
        bot.send_message(message.chat.id, film_info)
        film_info = ""
        iter += 1

    film_info = f"Вот {count} похожих на {curr_film_name} фильмы."
    markup.add(search_btn, filter_btn, saves_btn, help_btn)
    bot.send_message(message.chat.id, film_info, reply_markup=markup)
