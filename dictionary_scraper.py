"""
Скрипт для создания базы данных словаря.
Продуктом работы кода является база данных db.sqlite, участвующая в работе
телеграм-бота.
"""

import re
import sqlite3

import requests
from bs4 import BeautifulSoup


def update_db(content):
    """
    Функция записи собранных данных в БД.
    Запись в базу происходит пакетами по одной странице с сайта за итерацию.
    """
    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS nouns
        (
            word TEXT,
            length INTEGER
        );
        '''
    )

    cur.executemany('INSERT INTO nouns VALUES(?, ?);', content)

    con.commit()
    con.close()


def get_page(url):
    """Requests. Получение данных страницы."""
    with requests.Session() as session_scraping:
        session_scraping.headers = {
            'user-agent':
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
                "(KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"
        }
        response = session_scraping.get(url)
        return response.text


def word_filter(word):
    """
    Фильтр слов перед записью в базу данных.
    Исключить слова, содержащие *, -, заглавные буквы (имена собственные),
    слово 'я' ("я" - это слово по версии Эфремовой).
    """
    pattern = r'(-|[А-Я]|^я$)'
    pattern_look = re.search(pattern, word)
    if not pattern_look:
        return word
    return None


def word_cleaner(word):
    """Замена символов и букв в полученных словах."""
    word = word.replace('ё', 'е').replace(' *', '')
    word = word.strip()
    return word


def soup_scraper(html):
    """Парсинг данных. Запись в кортеж слово и его длинны."""
    soup = BeautifulSoup(html, 'lxml')
    words = soup.findAll('p')
    total_list = []

    for word in words:
        word = word.text.strip()
        if word_filter(word):
            data = (word_cleaner(word), len(word_cleaner(word)))
            total_list.append(data)

    update_db(total_list)


def main():
    """
    Генератор массива ссылок для существительных 3 родов.
    Для каждого из родов сбор букв в цикле от А до Я.
    """
    pattern = 'http://nskhuman.ru/unislov/suschestv.php?nrod={}&nlet={}'

    for word_part in range(1, 4):
        for letter in range(1, 34):
            url = pattern.format(str(word_part), str(letter))
            soup_scraper(get_page(url))


if __name__ == "__main__":
    main()
