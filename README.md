# Word_Hound - Телеграм бот-помощник для игры “Вордли”

## Описание
Ассистент для игры "Вордли" использует базу данных существительных для версий игры длиной от 5 до 9 букв. Алгоритм подбирает ответы на основе слов из словаря, содержащих определенные буквы.

Телеграм-бот позволяет выбрать тип игры в зависимости от длины искомого слова и предлагает 2-3 слова, которые пользователь должен ввести в игре. На следующем шаге пользователь должен сообщить Телеграм-боту, какие буквы были отмечены в игре как найденные. В ответ бот предложит одно или несколько возможных слов, которые будут являться правильным ответом.

### Основные пакеты:
- main.py - Сервис логики работы Telegram бота.
- word_search.py - Сервис анализа и подбора слов для игры “Вордли”.

### Дополнительные пакеты для кастомизации работы бота:
- dictionary_scraper.py - Скрипт для создания базы данных словаря. Продуктом работы кода является база данных db.sqlite, участвующая в работе телеграм-бота.
- key_words_analyser.py - Скрипт для поиска ключевых слов для группы слов с одинаковой длинной. В результате скрипт выводит в консоль группы слов, для каждой длинны букв,
с которых можно начинать работу по угадыванию слов в телеграм-боте.


### Технологии
- Python 3.9
- SQLite3
- TelegramBotAPI 4.10
- Dotenv 1.0
- RegEx

## Как запустить проект:

1. Скопируйте репозиторий и перейдите в него в командной строке:

```
git clone https://https://github.com/EugeniGrivtsov/word_hound-telegram_bot
```

```
cd word_hound-telegram_bot
```

2. Создайте и активируйте виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

3. Установите зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

4. Зарегистрируйте нового телеграм бота и создайте фаил '.env' в корне проекта:

```
TELEGRAM_TOKEN = '<токен_вашего_бота>'
```

5. Запустите проект:

```
python main.py
```
