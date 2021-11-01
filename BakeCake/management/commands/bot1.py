import logging
import time
import telegram
import re

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request

from BakeCake.models import Message
from BakeCake.models import Profile


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

MENU, LEVELS, FORM = range(3)

TG_TOKEN = settings.BOT_TOKEN

bot = telegram.Bot(token=TG_TOKEN)

menu_keyboard = [['Собрать торт'],
                 ['Параметры заказа'],
                 ['Статус заказа']
                 ]

menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True, one_time_keyboard=True)


def chunks_generators(buttons, chunks_number):
    for i in range(0, len(buttons), chunks_number):
        yield buttons[i: i + chunks_number]


def keyboard_maker(buttons, number):
    keyboard = list(chunks_generators(buttons, number))
    markup = ReplyKeyboardMarkup(keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    return markup


def bottons_parser(botton):
    return re.findall(r'\d+', botton)


def start(update, context):
    time.sleep(1)
    user = update.message.from_user
    text = f'Привет {user.first_name}, \nИзготовление тортов на заказ.\nВыберите ингредиенты, форму, основу, надпись, а мы привезем готовый торт к вашему празднику.'

    update.message.reply_text(text, reply_markup=menu_markup)
    context.user_data['chat_id'] = update.message.chat_id
    chat_id = update.message.chat_id

    context.user_data['first_name'] = update.message.from_user.first_name
    context.user_data['last_name'] = update.message.from_user.last_name   #null=True
    context.user_data['username'] = update.message.from_user.username
    profile,_ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name':update.message.from_user.username,
            'first_name':update.message.from_user.first_name,
            'last_name':update.message.from_user.last_name,
        }
    )

    Message(
        profile=profile,
        text=update.message.text
    ).save()

    return MENU

def menu(update, context):
    user_message = update.message.text
    if user_message == 'Собрать торт':
        buttons = ['1 уровень (+400р)', '2 уровня (+750р)', '3 уровня (+1100р)', 'Вернулся в меню']
        context.user_data['level_buttons'] = buttons[:-1]
        levels_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Количество уровней (обязательное поле)', reply_markup=levels_markup)
        return LEVELS
    if user_message == 'Параметры заказа':
        update.message.reply_text('Пока в разработке',
                                  reply_markup=menu_markup)
        return MENU
    elif user_message == 'Статус заказа':
        update.message.reply_text('Пока в разработке', reply_markup=menu_markup)
        return MENU
    else:
        update.message.reply_text('Пока в разработке',
                                  reply_markup=menu_markup)
        return MENU


def levels(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    if user_message in context.user_data.get('level_buttons'):
        total_levels, price = bottons_parser(user_message)
        context.user_data['total_levels'] = int(total_levels)
        context.user_data['price'] = int(price)
        print(int(total_levels) + int(price))
        buttons = ['Квадрат (+600)', 'Круг (+400)',
                   'Прямоугольник (+1000)', 'Вернулся в меню']
        context.user_data['form_buttons'] = buttons[:-1]
        levels_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Форма (обязательное поле)',
                                  reply_markup=levels_markup)
        return FORM
    else:
        pass

def form(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    if user_message in context.user_data.get('form_buttons'):
        price = bottons_parser(user_message)
        context.user_data['bc_form'] = user_message.split()[0]
        context.user_data['price'] = int(price[0])
        print(user_message.split()[0], price[0])
        buttons = ['Без топпинга (+0)', 'Белый соус (+200)',
                   'Карамельный сироп (+180)', 'Кленовый сироп (+200)',
                   'Клубничный сироп (+300)', 'Черничный сироп (+350)',
                   'Молочный шоколад (+200)','Вернулся в меню']
        context.user_data['topping_buttons'] = buttons[:-1]
        topping_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Топпинг (Обязательное поле)',
                                  reply_markup=topping_markup)
        return FORM
    else:
        pass








def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
    )
    return ConversationHandler.END


class Command(BaseCommand):
    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.BOT_TOKEN,

        )


        updater = Updater(TG_TOKEN, use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={

                MENU: [CommandHandler('start', start),
                        MessageHandler(Filters.text, menu)],

                LEVELS: [CommandHandler('start', start),
                            MessageHandler(Filters.text, levels)],

                FORM: [CommandHandler('start', start),
                         MessageHandler(Filters.text, form)],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()


#if __name__ == '__main__':
#    main()