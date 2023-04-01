"""
Скрипт для поиска ключевых слов для группы слов с одинаковой длинной.
Задача скрипта:
а. Выявить самые часто используемые буквы для группы слов с одинаковой длинной.
б. Составить из этих букв существительные.
Идея в том, чтобы начиная игру wordle - проверить наличие или отсутствие букв,
которые присутствуют в максимально большом количестве слов с одинаковой длинной.
А учитывая то, что в программе wordle нельзя написать рандомные буквы, то
мало найти часто используемые буквы, но надо из них составить 2-3 слова
(зависит от длинны искомого слова, так для 8 и 9 букв, можно использовать
2 стартовых слова.)
В результате скрипт выводит в консоль группы слов, для каждой длинны букв,
с которых можно начинать работу по угадыванию слов в телеграм-боте.
"""

import sqlite3

# введите искомую длину слова
word_length = 5

letter_limit = word_length * 3

def request_db():
    """
    Функуция возвращает весь перечень слов, соответствующий заданной
    длинне слова.
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
    (word_length,),
).fetchall()

con.close()


def unique_letter_words(word_list: list) -> list:
    """Исключает из списка слова с повторяющимися буквами."""
    for word in word_list[:]:
        if len(set(word)) < word_length:
            word_list.remove(word)
    return word_list


def most_frequent_letters(
    unique_letter_words: list, letter_limit: int = letter_limit
) -> list:
    """Самые популярные буквы, встречающихся в словах получаемого списка."""

    alphabet: dict = {}

    for word in unique_letter_words[:]:
        for letter in list(word):
            if (
                letter in alphabet
            ):  # счетчик количеcтва раз, когда буква встречается
                alphabet[letter] = alphabet[letter] + 1
            else:
                alphabet[letter] = 1  # если буква в первый раз встречается

    # сортировка словаря по значениям DESC
    alphabet: dict = dict(
        sorted(alphabet.items(), key=lambda item: item[1], reverse=True)
    )

    # первые ('letter_limit') ключей отсортированного словаря
    output = list(alphabet)[:letter_limit]

    return output


unique_letter_words: list = unique_letter_words(word_list)
first_letters_list: list = most_frequent_letters(word_list)

def word_search(unique_letter_words: list, first_letters_list: list):
    """
    Описание.
    """
    for word in unique_letter_words:
        if all(x in first_letters_list for x in set(word)):
            resulting_word_set = [word]
            second_letters_list = list(
                x for x in first_letters_list if x not in list(word)
            )
            for second_word in unique_letter_words:
                if second_word not in resulting_word_set:
                    if all(x in second_letters_list for x in set(second_word)):
                        third_letters_list = list(
                            x for x in second_letters_list if x not in list(second_word)
                        )
                        for third_word in unique_letter_words:
                            if third_word not in resulting_word_set:
                                if all(x in third_letters_list for x in set(third_word)):
                                    print([word, second_word, third_word])
                                    break

def main():
    """
    Описание.
    """

if __name__ == "__main__":
    main()