import telebot
from telebot import types
from config import SITE, ADMIN
from datetime import datetime
import sys
import locale

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bot = telebot.TeleBot('7338019969:AAHAGV9Mxgp0i2R3WW4xfc9m2_3da0CfA2U')


@bot.message_handler(commands=['start'])
def start(message):
    """
    Функция приветствует пользователя и предлагает ему выбор:
    1. Записаться на фотосессию.
    2. Заказать обратный звонок.
    3. Перейти на сайт.
    """
    markup = types.ReplyKeyboardMarkup(True)
    button_1 = types.KeyboardButton('Записаться на фотосессию')
    button_2 = types.KeyboardButton('Свяжитесь со мной')
    markup.row(button_1, button_2)
    button_3 = types.KeyboardButton('Перейти на сайт')
    markup.row(button_3)
    bot.send_message(message.chat.id, f'Приветствую, {message.from_user.first_name}!\n'
                                      'Я - виртуальный помощник фотостудии МАММА МИА.\n'
                                      'Давайте вместе выберем лучшую фотосессию для вашего малыша!\n'
                                      'Или вы хотите сначала изучить наш сайт?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, processing_start_click)


def processing_start_click(message):
    """
    Функция обрабатывает ответ пользователя на вопрос из меню /start и запускает дальнейшие действия по скрипту:
    1. "Записаться на фотосессию" - запускает меню выбора типа съёмки.
    2. "Заказать обратный звонок" - записывает данные Клиента в файл callback.txt
    и отправляет уведомление Клиенту и Администратору.
    3. "Перейти на сайт" - открывает активную ссылку на сайт.
    """
    match message.text:
        case 'Записаться на фотосессию':
            choose_photoshoot(message)
            bot.register_next_step_handler(message, choose_photoshoot)
        case 'Свяжитесь со мной':
            bot.send_message(message.chat.id,
                             'Спасибо за обращение в студию МАММА МИА!\n\n'
                             'Мы уже получили уведомление, и свяжемся с Вами в течение суток.')
            current_date = datetime.now().date()
            current_weekday = current_date.strftime('%A')
            current_time = datetime.now().time().strftime('%H:%M')
            with open('./data/callback.txt', 'a', encoding='UTF-8') as file:
                file.write(
                    f'Пользователь {message.from_user.username} '
                    f'({message.from_user.first_name} {message.from_user.last_name}) '
                    f'попросил связаться с ним {current_date} в {current_weekday} в {current_time}.\n')
            bot.send_message(ADMIN,
                                 f'Новый запрос на обратную связь от пользователя {message.from_user.username} '
                                 f'({message.from_user.first_name} {message.from_user.last_name}): '
                                 f'{current_date} в {current_weekday} в {current_time}')
            bot.register_next_step_handler(message, processing_start_click)
        case 'Перейти на сайт':
            go_to_site(message)
            bot.register_next_step_handler(message, processing_start_click)


def choose_photoshoot(message):
    """
    Функция предоставляет пользователю выбор услуги:
    1. NEWBORN.
    2. BABY.
    3. SMASH CAKE.
    4. Съёмка Крещения.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('🤱  NEWBORN', callback_data='newborn'),
               telebot.types.InlineKeyboardButton('👶  BABY', callback_data='baby'),
               telebot.types.InlineKeyboardButton('🎂  SMASH CAKE', callback_data='smash_cake'),
               telebot.types.InlineKeyboardButton('☦️  Съёмка Крещения', callback_data='christening'))
    markup.add(telebot.types.InlineKeyboardButton('Перейти на сайт', url=SITE))
    bot.send_message(message.chat.id,
                     f'Вас интересует фотосессия NEWBORN (для новорождённых) '
                     f'или BABY (для малышей до 2 лет)?',
                     reply_markup=markup)


def processing_choose_photoshoot(message):
    """
    Функция обрабатывает ответ пользователя на вопрос из меню /choose_photoshoot
    и запускает дальнейшие действия по скрипту:
    1. NEWBORN - выводит изображение и отправляет в меню выбора статуса малыша - "уже родился" или "в ожидании".
    2. BABY - выводит изображение и запрашивает дату рождения малыша, а после наличие пожеланий по времени съёмки.
    3. SMASH CAKE - выводит изображение и запрашивает дату рождения малыша. После отправляет в меню выбора формата
    съёмки: непосредственно в день рождения или заранее.
    4. Съёмка Крещения - выводит изображение и отправляет в меню, запрашивающее наличие конкретной даты и церкви.
    """
    match message.text:
        case 'newborn':
            newborn_client_record(message)
            bot.register_next_step_handler(message, newborn_client_record)
        case 'baby':
            baby_client_record(message)
            bot.register_next_step_handler(message, baby_client_record)
        case 'smash_cake':
            smash_cake_client_record(message)
            bot.register_next_step_handler(message, smash_cake_client_record)
        case 'christening':
            christening_client_record(message)
            bot.register_next_step_handler(message, christening_client_record)


def newborn_client_record(message):
    """
    Функция запрашивает у пользователя информацию о статусе рождения ребёнка для записи на фотосъёмку.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Уже родился', callback_data='borned'),
               telebot.types.InlineKeyboardButton('В ожидании', callback_data='waiting'))
    file = open('./data/jpg/newborn.jpg', 'rb')
    bot.send_message(message.chat.id, 'Ваш малыш уже родился или вы находитесь в ожидании?', reply_markup=markup)
    bot.send_photo(message.chat.id, file, reply_markup=markup)


def baby_client_record(message):
    """
    Функция запрашивает у пользователя информацию о пожеланиях по времени съёмки ребёнка для записи на фотосъёмку.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Я хочу съёмку в определённом возрасте', callback_data='is_wishes'),
               telebot.types.InlineKeyboardButton('В ближайшее время', callback_data='near_future'))
    file = open('./data/jpg/baby.jpg', 'rb')
    bot.send_message(message.chat.id, 'Вы хотели бы провести съёмку в ближайшее время или планируете её '
                                      'на определённый возраст/дату?', reply_markup=markup)
    bot.send_photo(message.chat.id, file)


def smash_cake_client_record(message):
    """
    Функция запрашивает у пользователя информацию о пожеланиях по поводу сроков проведения съёмки ребёнка
    для записи на фотосъёмку.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Заранее', callback_data='in_advance'),
               telebot.types.InlineKeyboardButton('В день рождения', callback_data='in_birthday'))
    file = open('./data/jpg/smash_cake.jpg', 'rb')
    bot.send_message(message.chat.id, 'Вы хотите провести съёмку заранее (чтобы получить готовые фотографии '
                                      'к празднику) или непосредственно в день рождения?', reply_markup=markup)
    bot.send_photo(message.chat.id, file)


def christening_client_record(message):
    """
    Функция запрашивает у пользователя информацию об этапе подготовки к таинству для записи на фотосъёмку.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Да', callback_data='booked'),
               telebot.types.InlineKeyboardButton('Нет, нужна консультация', callback_data='consultation'))
    file = open('./data/jpg/christening.jpg', 'rb')
    bot.send_message(message.chat.id, 'Вы уже выбрали дату и место проведения Таинства?', reply_markup=markup)
    bot.send_photo(message.chat.id, file)


def go_to_site(message):
    """
    Функция открывает активную ссылку на сайт.
    """
    bot.send_message(message.chat.id, SITE)


bot.polling(non_stop=True)
