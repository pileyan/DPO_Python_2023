import telebot
import random
import pandas as pd
from matplotlib.cbook import flatten
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

df = pd.read_csv('news_plus_1.csv', sep = ';')

def get_themes():
    return ', '.join(sorted(set(flatten([i.split(', ') for i in df.themes.unique()]))))

# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, """\
Привет, я умею читать статьи с nplus1.ru.
Если хотите посмотреть темы статей, введите /themes.\n\
Если хотите прочитать какую-либо статью в зависимости от категории, \
введите Категории и далее – категории через запятую, например\
Категории IT, Палеонтология и бот пришлет случайную статью на эту тему.
""")

@bot.message_handler(func=lambda message: message.text.strip().lower().startswith('категории'))
def send_article(message):
    category = random.choice([i.lower().strip() for i in message.text[9:].split(',')])
    article = df[df.themes.apply(lambda x: category in x.lower().split(', '))]
    if len(article) == 0:
        bot.send_message(message.chat.id, 'Нет такой категории. Список категорий смотреть тут: /themes')
    else:
        sampled = article.sample(1)
        article_text = sampled.full_text.values[0]
        if len(article_text) <= 4096:
            bot.send_message(message.chat.id, article_text)
        else:
            elements = article_text.split('\n')
            for el in elements:
                bot.send_message(message.chat.id, el)
        bot.send_message(message.chat.id, sampled.url.values[0])

@bot.message_handler(commands=['categories'])
def send_categories(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = telebot.types.KeyboardButton('категории Физика')
    itembtn2 = telebot.types.KeyboardButton('категории Математика')
    itembtn3 = telebot.types.KeyboardButton('категории Зоология')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите тему:", reply_markup=markup)

# Handle '/themes'
@bot.message_handler(commands=['themes'])
def send_themes(message):
    bot.send_message(message.chat.id,
                     get_themes())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.chat.id, 'Не понимаю. Чтобы узнать о функциональности бота введите /help')


bot.infinity_polling()
