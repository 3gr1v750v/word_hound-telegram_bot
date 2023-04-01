import os
import re

import telebot
from dotenv import load_dotenv
from telebot import types

from word_search import KEY_WORDS, word_finder_main_search

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def join_list(content_list):
    return "\n".join(content_list)


@bot.message_handler(commands=['start'])
def start(message):
    """
    Стартовая команда. Показывает интро текст и две интерфейсные кнопки.
    """
    intro_text = (
        'Вас приветствует программа-ассистент для игры по угадыванию слов!\n\n'
        'Перед тем, как начать, пожалуйста ознакомьтесь с <b>инструкцией</b> '
        '(одноименная кнопка должна появиться в интерфейсе ниже).'
        '\n\n Перезапустить бота можно командой <i>/start</i>'
    )

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1, one_time_keyboard=True
    )
    choose_game = types.KeyboardButton('Выбрать Игру')
    instructions = types.KeyboardButton('Инструкция')
    markup.add(choose_game, instructions)

    bot.send_message(
        message.chat.id, intro_text, parse_mode='html', reply_markup=markup
    )


@bot.message_handler(
    content_types=['text'], func=lambda message: message.text == 'Инструкция'
)
def instruction(message):
    """
    Инструкция по работе с приложением бота (модуль: word_search.py).
    Содержит текстовое описание и отрисовка одной кнопки интерфейса.
    """
    text = (
        '<b>ИНСТРУКЦИЯ:</b>\n\nКогда вы выберете игру с определенной длинной '
        'слова, телеграм бот предложит вам ввести 2-3 слова в интерфейс игры, '
        'в которой вы непосредственно играете.\n<b>Не надо вводить эти '
        'слова в чат бота. Бот уже заранее знает про них :)</b>'
    )
    bot.send_message(message.chat.id, text, parse_mode='html')

    photo = open('static/img/game_instructions.png', 'rb')
    bot.send_photo(message.chat.id, photo)

    text2 = (
        'В зависимости от программы, в которой вы играете, цвета могут немного'
        ' различаться, но смысл смысл сохранятеся:\n<b>Буква выделена серым '
        'цветом</b> - такой буквы нет в искомом слове.\n<b>Буква выделена '
        'желтым цветом</b> - буква есть в искомом слове, но она стоит не на '
        'своём месте.\n<b>Буква выделена зеленым цветом</b> - буква есть в '
        'искомом слове и она на стоит на своем месте. \n\nТеперь, когда игра '
        'вам показала найденные буквы, запишите их в телеграм чат следующим '
        'образом (порядок букв неважен):\n<b>Буква "к" выделена желтым '
        'цветом</b> запишите её в нижнем регистре <b>"к"</b>\n<b>Буква "и" '
        'выделена зеленым цветом</b> запишите её в верхнем регистре '
        '<b>"И"</b>\n\nВ результате для конкретного примера у вас должно '
        'получиться <b>"контИ"</b> (напомню, что порядок букв не важен'
        ', можете написать хоть <b>"нИтко"</b>, хоть <b>"Инокт"</b>)\n\n'
        'Введите в телеграм бот те буквы, что игра вам подсветила, '
        'как найденные, а дальше программа бота подберёт слово (или слова), '
        'которое будет правильным ответом.'
    )

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1, one_time_keyboard=True
    )
    choose_game = types.KeyboardButton('Выбрать Игру')
    markup.add(choose_game)
    bot.send_message(
        message.chat.id, text2, parse_mode='html', reply_markup=markup
    )


@bot.message_handler(
    content_types=['text'], func=lambda message: message.text == 'Выбрать Игру'
)
def choose_game(message):
    """
    Inline меню - выбор игры.
    Функция check_chose_game_callback_data перехватывает нажатие кнопок меню.
    """
    text = 'Выберите игру, в которую вы хотите сыграть:'
    markup = types.InlineKeyboardMarkup(row_width=1)
    five_letters = types.InlineKeyboardButton(
        text='Слово из 5 букв', callback_data='5letters'
    )
    six_letters = types.InlineKeyboardButton(
        text='Слово из 6 букв', callback_data='6letters'
    )
    seven_letters = types.InlineKeyboardButton(
        text='Слово из 7 букв', callback_data='7letters'
    )
    eight_letters = types.InlineKeyboardButton(
        text='Слово из 8 букв', callback_data='8letters'
    )
    nine_letters = types.InlineKeyboardButton(
        text='Слово из 9 букв', callback_data='9letters'
    )
    markup.add(
        five_letters, six_letters, seven_letters, eight_letters, nine_letters
    )
    bot.send_message(
        message.chat.id, text, parse_mode='html', reply_markup=markup
    )


listing = {'game_type': None, 'context': None}


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_chose_game_callback_data(callback):
    """
    Функция перехватывает нажатие кнопок choose_game фукнкции.
    В зависимости от нажатой кнопки, пользователю отправляется сообщение,
    параллельно название кнопки и текст сообщения сохраняются во внешний
    словарь для переиспользования в функции repeat.
    Запуск цикла проверки введённых данных о слове.
    """
    instructions: dict = {
        '5letters': (f'Введите следующие слова в интерфейс игры:\n'
                     f'<b>{join_list(KEY_WORDS[5])}</b>\n\nНапишите отмеченные'
                     f' игрой буквы в чат бота.\n\nНапример:\n<b>кОр</b>'),
        '6letters': (f'Введите следующие слова в интерфейс игры:\n'
                     f'<b>{join_list(KEY_WORDS[6])}</b>\n\nНапишите отмеченные'
                     f' игрой буквы в чат бота.\n\nНапример:\n<b>ЕКол</b>'),
        '7letters': (f'Введите следующие слова в интерфейс игры:\n'
                     f'<b>{join_list(KEY_WORDS[7])}</b>\n\nНапишите отмеченные'
                     f'игрой буквы в чат бота.\n\nНапример:\n<b>рсльеА</b>'),
        '8letters': (f'Введите следующие слова в интерфейс игры:\n'
                     f'<b>{join_list(KEY_WORDS[8])}</b>\n\nНапишите отмеченные'
                     f'игрой буквы в чат бота.\n\nНапример:\n<b>тека</b>'),
        '9letters': (f'Введите следующие слова в интерфейс игры:\n'
                     f'<b>{join_list(KEY_WORDS[9])}</b>\n\nНапишите отмеченные'
                     f'игрой буквы в чат бота.\n\nНапример:\n<b>дрбоуте</b>'),
    }

    listing['game_type'] = callback.data
    listing['repeat'] = instructions[callback.data]

    sent = bot.send_message(
        callback.message.chat.id,
        instructions[callback.data],
        parse_mode='html',
    )
    bot.register_next_step_handler(sent, input_validator)


@bot.message_handler(
    content_types=['text'], func=lambda message: message.text == 'Повторить'
)
def repeat(message):
    """
    Условно повторяет действия функции check_chose_game_callback_data.
    Только берёт данные из внешнего словаря и перезапускает цикл проверки
    данных о слове.
    """
    sent = bot.send_message(
        message.chat.id, listing['repeat'], parse_mode='html'
    )
    bot.register_next_step_handler(sent, input_validator)


def input_validator(message):
    """
    Цикл проверки введённых данных о слове.
    - Слово должно содержать только буквы русского алфавита в количестве не
    больше, чем длинна слова игры.
    - Слово не должно быть копий слова, которое надо ввести во внешнюю игру.
    Если два вышеуказанных условия не выполняются, цикл проверки
    перезапускается. В случае выполнения, включается модуль word_search.py
    и подбирается слово. По завершению игры в интерфейсе отрисовываются
    кнопки меню для повтора или выбора другой игры.
    """
    number_of_letters = int(listing['game_type'][0])
    letters = message.text.replace(" ", "")

    # regex validation
    pattern = r'^[А-я]{1,' + f'{number_of_letters}' + r'}$'
    pattern_look = re.search(pattern, letters)

    if not pattern_look:
        text = (f'Искомое слово не может быть длиннее {number_of_letters} '
                f'символов и должно содержать только буквы русского алфавита.')
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, input_validator)
        return
    elif letters.lower() in KEY_WORDS[int(listing['game_type'][0])]:
        text = (f'Пожалуйста ознакомьтесь с инструкцией. Здесь писать исходные'
                f' слова не надо, напишите только буквы, которые вам '
                f'программа, в которой вы играете, отметила как найденные.\n\n'
                f'Если вы просто хотите посмотреть, как работает программа, '
                f'введите буквы из примера, что написан выше. '
                f'Соблюдайте регистр.')
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, input_validator)
        return
    else:
        output_result = word_finder_main_search(number_of_letters, letters)
        html_output = join_list(output_result)

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=1, one_time_keyboard=True
        )
        repeat = types.KeyboardButton("Повторить")
        choose_game = types.KeyboardButton("Выбрать Игру")
        markup.add(choose_game, repeat)

        if output_result:
            if len(output_result) > 1:
                bot.send_message(
                    message.chat.id,
                    (f"Правильным ответом является одно из "
                     f"{len(output_result)} слов:"),
                )
            else:
                bot.send_message(message.chat.id, f"Правильный ответ:")
            bot.send_message(
                message.chat.id,
                f'<b>{html_output}</b>',
                parse_mode='html',
                reply_markup=markup,
            )
        else:
            bot.send_message(
                message.chat.id,
                (f"К сожалению ни одного слова не найдено.\nПожалуйста, "
                 f"проверьте вводимые буквы и их регистр."),
                reply_markup=markup,
            )
            bot.register_next_step_handler(message, input_validator)


bot.polling()

if __name__ == '__main__':
    start()
