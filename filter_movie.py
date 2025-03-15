import telebot
from telebot import types

from kinopoisk_unofficial.kinopoisk_api_client import KinopoiskApiClient
from kinopoisk_unofficial.model.filter_country import FilterCountry
from kinopoisk_unofficial.model.filter_order import FilterOrder
from kinopoisk_unofficial.model.filter_genre import FilterGenre
from kinopoisk_unofficial.request.films.film_search_by_filters_request import FilmSearchByFiltersRequest


api_client = KinopoiskApiClient("api-token")
bot = telebot.TeleBot('tg-token')

genre = None
year = 0
rating = 0.0
country = None


def process_genre_step(message):
    global genre
    genre = str(message.text)
    msg = bot.send_message(message.chat.id, "С какого года искать?")
    bot.register_next_step_handler(msg, process_year_step)


def process_year_step(message):
    global year
    year = int(message.text)
    msg = bot.send_message(message.chat.id, "Минимальный рейтинг (от 1 до 10)?")
    bot.register_next_step_handler(msg, process_rating_step)


def process_rating_step(message):
    global rating
    rating = float(message.text)
    msg = bot.send_message(message.chat.id, "Страна производства?")
    bot.register_next_step_handler(msg, process_country_step)


def process_country_step(message):
    global country
    global genre
    global year
    global rating
    country = message.text

    request = FilmSearchByFiltersRequest()
    request.year_from = year
    request.rating_from = rating
    request.order = FilterOrder.NUM_VOTE
    request.add_genre(FilterGenre(1, genre))
    request.add_country(FilterCountry(1, country))

    # Выполнить запрос с использованием фильтров и обрабатывать результаты, например:
    films = api_client.films.send_film_search_by_filters_request(request)
    film_info = ""
    iter = 1
    for film in films.items[:5]:
        # форматирование информации о фильме
        film_info += f"#{iter} : {film.name_ru}\n" \
                     f"Год: {film.year}\n" \
                     f"Рейтинг: {film.rating_kinopoisk}\n" \
                     f"Постер фильма: {film.poster_url_preview}\n\n"
        bot.send_message(message.chat.id, film_info)
        film_info = ""
        iter += 1

    markup = types.InlineKeyboardMarkup(row_width=2)

    search_btn = types.InlineKeyboardButton("🔍 Найти фильм", callback_data='search')
    filter_btn = types.InlineKeyboardButton("🔍 Подобрать фильм по критериям", callback_data='filter')
    help_btn = types.InlineKeyboardButton("❓ Что ты умеешь?", callback_data='help')
    markup.add(search_btn, filter_btn, help_btn)

    film_info = f"Вот фильмы по вашему критерию из КиноПоиска"
    bot.send_message(message.chat.id, film_info, reply_markup=markup)


bot.polling()
