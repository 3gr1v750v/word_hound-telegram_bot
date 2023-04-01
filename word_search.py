import sqlite3
from re import match

# Стартовые слова с уникальными буквами для каждого типа игры.
KEY_WORDS: dict = {
    5: ['кумир', 'сплав', 'бетон'],
    6: ['бедняк', 'пароль', 'висмут'],
    7: ['бульдог', 'язычник', 'расцвет'],
    8: ['тумбочка', 'шпиндель'],
    9: ['дряблость', 'кампучиец'],
}


def sqlite_export(search_word_length: int) -> list:
    """
    База данных содержит слово и его длину.
    По запросу из базы данных выгружаются в список(!) все слова определенной
    длинны.
    """
    con = sqlite3.connect('db.sqlite')
    con.row_factory = lambda cursor, row: row[0]
    cur = con.cursor()

    word_list = cur.execute(
        '''
    SELECT word
    FROM nouns
    WHERE length = ?;
    ''',
        (search_word_length,),
    ).fetchall()

    con.close()
    return word_list


def regex_generator(
    action_words_list: list, existing_letters: list, low_existing_letters: list
) -> list:
    """
    Создание паттерна регулярного выражения, для фильтрации списка слов.
    Для каждого слова из словаря KEY_WORDS для определенного типа игры,
    каждая буква сравнивается с входящими данными и формируется паттерн по
    следующим правилам:
    - строчное написание ('а') - на этом месте в искомом слове может быть любая
    буква кроме 'а'
    - заглавное написание ('Е') - на этом месте в искомом слове стоит буква 'е'
    - если совпадений не найдено - возвращается символ '.'
    Например: Слово 'кумир', входящие данные 'Миан' - буквы 'М' и 'и' есть в
    слове, остальные игнорируются. Получается паттерн "..[м][^и]."
    В результате получаем количество паттернов в списке, равное количеству слов
    в словаре KEY_WORDS для определенного типа игры.
    """

    pattern_list: list = []

    for wrd in range(len(action_words_list)):
        pattern: str = ''
        for itr in range(len(action_words_list[0])):
            if action_words_list[wrd][itr] in low_existing_letters:
                if (
                    action_words_list[wrd][itr].upper()
                    in existing_letters[
                        low_existing_letters.index(action_words_list[wrd][itr])
                    ]
                ):
                    pattern = pattern + f'[{action_words_list[wrd][itr]}]'
                else:
                    pattern = pattern + f'[^{action_words_list[wrd][itr]}]'
            else:
                pattern = pattern + '.'
        pattern_list.append(pattern)

    return pattern_list


def word_finder_main_search(
    search_word_length: int, existing_letters: str
) -> list:
    """
    Основная управляющая функция для поиска и анализа слов.
    Производит серию фильтраций списка слов, полученных из базы данных,
    сначала убирая слова, в которых есть буквы, гарантированно отсутствующие,
    потом оставляя слова с буквами, которые должны присутствовать. В конце
    производится фильтрация оставшихся слов на основе серии регулярных
    выражений.
    """

    # Конвертация стринга входящего сообщения в список по буквам.
    existing_letters: list = list(existing_letters)

    # Конвертация списка стартовых слов в список букв.
    popular_letters: list = list("".join(KEY_WORDS[search_word_length]))

    # Копия списка existing_letters но в нижнем регистре.
    low_existing_letters: list = list("".join(existing_letters).lower())

    # Передаём стартовые слова в отдельный список.
    action_words_list: list = KEY_WORDS[search_word_length]

    # Исключить из списка букв, те, которые отмечены как присутствующие.
    odd_letters: list = [
        x for x in popular_letters if x not in low_existing_letters
    ]

    # Экспорт списка слов из БД sqlite.
    word_list: list = sqlite_export(search_word_length)

    # Убираем из списка слова, в которых есть отсутствующие буквы.
    for word in word_list[:]:
        for letter in word:
            if letter in odd_letters:
                word_list.remove(word)
                break

    # Оставляем только слова, в которых присутствуют отмеченные буквы.
    filtered_list: list = [
        word
        for word in word_list
        if all(letter in word for letter in low_existing_letters)
    ]

    # Получаем паттерны regex для финальной фильтрации списка слов.
    pattern_list: list = regex_generator(
        action_words_list, existing_letters, low_existing_letters
    )

    # Оставляем в только те слова, которе прошли regex фильтрацию.
    for pattern in pattern_list:
        filtered_list = list(
            filter(lambda v: match(pattern, v), filtered_list)
        )

    return filtered_list


if __name__ == '__main__':
    word_finder_main_search()
