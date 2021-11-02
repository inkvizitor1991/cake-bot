import logging
import time
import telegram
import re

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request

from BakeCake.models import Order
from BakeCake.models import Profile
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
# from order import get_order_text check_date_time
from BakeCake.management.commands.order import get_order_text, test_phone
from BakeCake.management.commands.check_date_time import check_time, \
    check_date, get_datetime
from BakeCake.management.commands.get_price import get_price
from BakeCake.management.commands.get_address import get_adress

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

MENU, LEVELS, FORM, TOPPING, BERRIES, DECOR, INSCRIPTION, COMMENT, PROMO, ADDRESS, DELIVERY_DATE, DELIVERY_TIME, ORDER, PERSONAL_DATA, PHONE, REG_ADDRESS, CREATED_ORDER = range(17)

TG_TOKEN = settings.BOT_TOKEN

bot = telegram.Bot(token=TG_TOKEN)

menu_keyboard = [['Собрать торт'],
                 ['Мои заказы']
                 ]

back_buttons = ['Пропустить', 'Назад', 'Вернулся в меню']
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True,
                                  one_time_keyboard=True)


def chunks_generators(buttons, chunks_number):
    for button in range(0, len(buttons), chunks_number):
        yield buttons[button: button + chunks_number]


def keyboard_maker(buttons, number):
    keyboard = list(chunks_generators(buttons, number))
    markup = ReplyKeyboardMarkup(keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    return markup


def start(update, context):
    time.sleep(1)
    user = update.message.from_user
    text = f'Привет {user.first_name}, \nИзготовление тортов на заказ.\nВыберите ингредиенты, форму, основу, надпись, а мы привезем готовый торт к вашему празднику.'
    update.message.reply_text(text)
    chat_id = update.message.chat_id
    context.user_data['user_id'] = update.message.chat_id
    context.user_data['first_name'] = update.message.from_user.first_name
    context.user_data['last_name'] = update.message.from_user.last_name
    context.user_data['username'] = update.message.from_user.username
    check_user = Profile.objects.filter(external_id=chat_id).exists()
    if check_user:
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU

    else:
        buttons = ['Согласен', 'Не согласен']
        personal_data_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        name = 'approval.pdf'
        bot.send_document(chat_id=chat_id,
                          document=open(f'BakeCake/management/commands/{name}',
                                        'rb'))
        update.message.reply_text(
            'Ваше согласие на обработку персональных данных',
            reply_markup=personal_data_markup)
        return PERSONAL_DATA


def personal_data(update, context):
    user_message = update.message.text
    if user_message == 'Согласен':
        update.message.reply_text('Введите ваш контактный телефон')
        contact_button = KeyboardButton('Отправить мой телефон',
                                        request_contact=True)
        my_keyboard = ReplyKeyboardMarkup(
            [[contact_button]], resize_keyboard=True)
        update.message.reply_text('Ваш контактный телефон',
                                  reply_markup=my_keyboard)
        return PHONE
    elif user_message == 'Не согласен':
        buttons = ['Согласен', 'Не согласен']
        personal_data_markup = keyboard_maker(buttons, 2)
        update.message.reply_text('Мое дело предложить - Ваше отказаться',
                                  reply_markup=personal_data_markup)
    else:
        pass


def phone(update, context):
    context.user_data['phone'] = update.message.contact['phone_number']
    update.message.reply_text(
        f'{update.message.chat.first_name}, ваши контактные данные сохранены!')
    update.message.reply_text('Введите свой адрес',
                              reply_markup=ReplyKeyboardRemove())
    return REG_ADDRESS


def reg_address(update, context):
    user_message = update.message.text
    context.user_data['reg_address'] = user_message
    buttons = ['Собрать торт']
    input_markup = keyboard_maker(buttons, 2)
    update.message.reply_text('Вы успешно зарегистрированы')
    time.sleep(0.5)
    update.message.reply_text('Собери свой первый торт',
                              reply_markup=input_markup)
    return MENU


def menu(update, context):
    chat_id = update.message.chat_id
    user_message = update.message.text
    if user_message == 'Собрать торт':
        buttons = ['Один уровень', 'Два уровня', 'Три уровня',
                   'Вернулся в меню']
        context.user_data['level_buttons'] = buttons
        levels_markup = keyboard_maker(buttons, 3)
        time.sleep(0.5)
        update.message.reply_text('Количество уровней',
                                  reply_markup=levels_markup)
        return LEVELS
    elif user_message == 'Мои заказы':
        check_user = Profile.objects.filter(external_id=chat_id).exists()
        get_price(chat_id)
        if check_user:
            all_orders = get_price(chat_id)
            context.user_data['all_orders'] = all_orders
            buttons = ['Вернулся в меню']
            if len(all_orders) > 1:
                buttons.append('Следующий заказ')
            created_orders_markup = keyboard_maker(buttons, 2)
            update.message.reply_text(f'{all_orders[0]}',
                                      reply_markup=created_orders_markup)
            return CREATED_ORDER
        else:
            update.message.reply_text('У вас заказов нет',
                                      reply_markup=menu_markup)
            return MENU
    else:
        update.message.reply_text('Следующий заказ',
                                  reply_markup=menu_markup)
        return MENU


def created_orders(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    if user_message == 'Следующий заказ':
        all_orders = context.user_data.get('all_orders')
        update.message.reply_text(f'{all_orders[1]}',
                                  reply_markup=menu_markup)
        return MENU


def levels(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    if user_message in context.user_data.get('level_buttons')[:-1]:
        context.user_data['total_levels'] = user_message
        buttons = ['Квадрат', 'Круг', 'Прямоугольник', 'Назад',
                   'Вернулся в меню']
        context.user_data['form_buttons'] = buttons
        levels_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Форма',
                                  reply_markup=levels_markup)
        return FORM


def form(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = context.user_data.get('level_buttons')
        levels_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Количество уровней',
                                  reply_markup=levels_markup)
        return LEVELS
    elif user_message in context.user_data.get('form_buttons')[:-2]:
        context.user_data['bc_form'] = user_message
        buttons = ['Без топпинга', 'Белый соус', 'Карамельный сироп',
                   'Кленовый сироп', 'Клубничный сироп', 'Черничный сироп',
                   'Молочный шоколад', 'Назад', 'Вернулся в меню']
        context.user_data['topping_buttons'] = buttons
        topping_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Топпинг',
                                  reply_markup=topping_markup)
        return TOPPING


def topping(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = context.user_data.get('form_buttons')
        form_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Форма',
                                  reply_markup=form_markup)
        return FORM
    elif user_message in context.user_data.get('topping_buttons')[:-2]:
        context.user_data['bc_topping'] = user_message
        buttons = ['Ежевика', 'Клубника', 'Малина', 'Голубика',
                   'Пропустить', 'Назад', 'Вернулся в меню']
        context.user_data['berries_buttons'] = buttons
        berries_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Ягоды',
                                  reply_markup=berries_markup)
        return BERRIES
    else:
        pass


def berries(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = context.user_data.get('topping_buttons')
        topping_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Топпинг',
                                  reply_markup=topping_markup)
        return TOPPING
    elif user_message in context.user_data.get('berries_buttons')[:-2]:
        context.user_data['bc_berries'] = user_message
        buttons = ['Маршмеллоу', 'Фисташки', 'Безе',
                   'Фундук', 'Пекан', 'Пропустить',
                   'Назад', 'Вернулся в меню']
        context.user_data['decor_buttons'] = buttons
        decor_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Декор',
                                  reply_markup=decor_markup)
        return DECOR


def decor(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = context.user_data.get('berries_buttons')
        berries_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Ягоды',
                                  reply_markup=berries_markup)
        return BERRIES
    elif user_message in context.user_data.get('decor_buttons')[:-2]:
        context.user_data['bc_decor'] = user_message
        buttons = ['Пропустить', 'Назад',
                   'Вернулся в меню']
        decor_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Надпись')
        time.sleep(0.5)
        update.message.reply_text(
            'Мы можем разместить на торте любую надпись, например: «С днем рождения!»',
            reply_markup=decor_markup)
        return INSCRIPTION
    else:
        pass


def inscription(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = context.user_data.get('decor_buttons')
        decor_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Декор',
                                  reply_markup=decor_markup)
        return DECOR
    else:
        context.user_data['price'] = 500
        context.user_data['bc_inscription'] = user_message
        if user_message == 'Пропустить':
            context.user_data['price'] = 0
        comment_markup = keyboard_maker(back_buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Комментарий к заказу',
                                  reply_markup=comment_markup)
        return COMMENT


def comment(update, context):
    user_message = update.message.text
    inscription_markup = keyboard_maker(back_buttons, 2)
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        time.sleep(0.5)
        update.message.reply_text(
            'Мы можем разместить на торте любую надпись, например: «С днем рождения!»',
            reply_markup=inscription_markup)
        return INSCRIPTION
    else:
        context.user_data['bc_comment'] = user_message
        update.message.reply_text('Введите промокод',
                                  reply_markup=inscription_markup)
        return PROMO


def promo(update, context):
    user_message = update.message.text
    buttons = ['Подтверждаю', 'Назад', 'Вернулся в меню']
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    if user_message == 'BakeCake200' or user_message == 'Пропустить':
        context.user_data['promo_code'] = user_message
        delivery_date_markup = keyboard_maker(buttons, 2)
        reg_address = context.user_data.get('reg_address')
        if not reg_address:
            reg_address = get_adress(update.message.chat_id)
            context.user_data['reg_address'] = reg_address
        time.sleep(0.5)
        update.message.reply_text(f'Адрес доставки:\n{reg_address}')
        update.message.reply_text(
            'Подтвердите адрес доставки или введите другой',
            reply_markup=delivery_date_markup)
        return ADDRESS
    else:
        promo_markup = keyboard_maker(back_buttons, 2)
        update.message.reply_text('Введите правильный промокод',
                                  reply_markup=promo_markup)
        return PROMO


def address(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        comment_markup = keyboard_maker(back_buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Введите промокод',
                                  reply_markup=comment_markup)
        return PROMO
    elif user_message == 'Подтверждаю':
        reg_address = context.user_data.get('reg_address')
        context.user_data['bc_address'] = reg_address
        buttons = ['Назад', 'Вернулся в меню']
        address_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Введите дату доставки(пример: 2021-10-27',
                                  reply_markup=address_markup)
        return DELIVERY_DATE
    else:
        context.user_data['bc_address'] = user_message
        buttons = ['Назад', 'Вернулся в меню']
        address_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Введите дату доставки(пример: 2021-10-27)',
                                  reply_markup=address_markup)
        return DELIVERY_DATE


def delivery_date(update, context):
    user_message = update.message.text
    buttons = ['Назад', 'Вернулся в меню']
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        address_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Введите дату доставки(пример: 2021-10-27',
                                  reply_markup=address_markup)
        return ADDRESS
    else:
        if get_datetime(user_message):
            context.user_data['bc_delivery_date'] = user_message
            delivery_date_markup = keyboard_maker(buttons, 2)
            time.sleep(0.5)
            update.message.reply_text('Введите время доставки(пример: 13:43)',
                                      reply_markup=delivery_date_markup)
            return DELIVERY_TIME
        else:
            update.message.reply_text('Введена не корректная дата.')
            buttons = ['Назад', 'Вернулся в меню']
            address_markup = keyboard_maker(buttons, 2)
            time.sleep(0.5)
            update.message.reply_text(
                'Введите дату доставки(пример: 2021-10-27)',
                reply_markup=address_markup)
            return DELIVERY_DATE


def delivery_time(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = ['Назад', 'Вернулся в меню']
        delivery_date_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Дата доставки',
                                  reply_markup=delivery_date_markup)
        return DELIVERY_DATE
    else:
        bc_delivery_date = context.user_data.get('bc_delivery_date')
        verified_datetime = get_datetime(bc_delivery_date, user_message)
        if verified_datetime == 'С тебя +20% за скорость':
            bc_speed = 20
            context.user_data['bc_speed'] = bc_speed
            update.message.reply_text(verified_datetime)
        else:
            context.user_data['bc_speed'] = 0
        if verified_datetime:
            context.user_data['bc_delivery_time'] = user_message
            buttons = ['Заказать торт', 'Назад', 'Вернулся в меню']
            delivery_time_markup = keyboard_maker(buttons, 2)
            time.sleep(0.5)
            total_levels = context.user_data.get('total_levels')
            bc_form = context.user_data.get('bc_form')
            bc_topping = context.user_data.get('bc_topping')
            bc_berries = context.user_data.get('bc_berries')
            bc_decor = context.user_data.get('bc_decor')
            bc_inscription = context.user_data.get('bc_inscription')
            bc_comment = context.user_data.get('bc_comment')
            bc_address = context.user_data.get('bc_address')
            bc_delivery_date = context.user_data.get('bc_delivery_date')
            bc_delivery_time = context.user_data.get('bc_delivery_time')
            promo_code = context.user_data.get('promo_code')
            bc_speed = context.user_data.get('bc_speed')
            new_order = [total_levels, bc_form, bc_topping, bc_berries,
                         bc_decor, bc_inscription, bc_comment, bc_address,
                         bc_delivery_date, bc_delivery_time,
                         promo_code, bc_speed]
            order_text, delivery, order_price = get_order_text(new_order)
            update.message.reply_text(order_text)
            update.message.reply_text(order_price)
            update.message.reply_text(delivery,
                                      reply_markup=delivery_time_markup)
            return ORDER
        else:
            update.message.reply_text('Введено некорректное время.')
            buttons = ['Назад', 'Вернулся в меню']
            address_markup = keyboard_maker(buttons, 2)
            time.sleep(0.5)
            update.message.reply_text('Введите время доставки(пример: 13:43)',
                                      reply_markup=address_markup)
            return DELIVERY_TIME


def order(update, context):
    user_message = update.message.text
    if user_message == 'Вернулся в меню':
        update.message.reply_text('Меню', reply_markup=menu_markup)
        return MENU
    elif user_message == 'Назад':
        buttons = ['Назад', 'Вернулся в меню']
        delivery_time_markup = keyboard_maker(buttons, 2)
        time.sleep(0.5)
        update.message.reply_text('Введите время доставки(пример: 13:43)',
                                  reply_markup=delivery_time_markup)
        return DELIVERY_TIME
    elif user_message == 'Заказать торт':
        time.sleep(0.5)
        update.message.reply_text('Ваш заказ успешно принят',
                                  reply_markup=menu_markup)
        chat_id = update.message.chat_id
        first_name = context.user_data.get('first_name')
        last_name = context.user_data.get('last_name')
        username = context.user_data.get('username')
        phone = context.user_data.get('phone')

        total_levels = context.user_data.get('total_levels')
        form = context.user_data.get('bc_form')
        topping = context.user_data.get('bc_topping')
        berries = context.user_data.get('bc_berries')
        decor = context.user_data.get('bc_decor')
        title = context.user_data.get('bc_inscription')
        comment = context.user_data.get('bc_comment')
        address = context.user_data.get('bc_address')
        delivery_date = context.user_data.get('bc_delivery_date')
        delivery_time = context.user_data.get('bc_delivery_time')
        if berries == 'Пропустить':
            berries = 'Не выбрано'
        if decor == 'Пропустить':
            decor = 'Не выбрано'
        if title == 'Пропустить':
            title = 'Не выбрано'
        if comment == 'Пропустить':
            comment = 'Не выбрано'
        profile, _ = Profile.objects.get_or_create(
            external_id=chat_id,
            defaults={
                'name': username,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone
            }
        )

        Order(
            profile=profile,
            number_levels=total_levels,
            form=form,
            topping=topping,
            berries=berries,
            decor=decor,
            title=title,
            comment=comment,
            address=address,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
        ).save()
        return MENU


def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
    )
    return ConversationHandler.END


class Command(BaseCommand):
    def handle(self, *args, **options):
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

                TOPPING: [CommandHandler('start', start),
                          MessageHandler(Filters.text, topping)],

                BERRIES: [CommandHandler('start', start),
                          MessageHandler(Filters.text, berries)],

                DECOR: [CommandHandler('start', start),
                        MessageHandler(Filters.text, decor)],

                COMMENT: [CommandHandler('start', start),
                          MessageHandler(Filters.text, comment)],

                ADDRESS: [CommandHandler('start', start),
                          MessageHandler(Filters.text, address)],

                INSCRIPTION: [CommandHandler('start', start),
                              MessageHandler(Filters.text, inscription)],

                DELIVERY_DATE: [CommandHandler('start', start),
                                MessageHandler(Filters.text, delivery_date)],

                DELIVERY_TIME: [CommandHandler('start', start),
                                MessageHandler(Filters.text, delivery_time)],

                ORDER: [CommandHandler('start', start),
                        MessageHandler(Filters.text, order)],

                PERSONAL_DATA: [CommandHandler('start', start),
                                MessageHandler(Filters.text, personal_data)],

                PHONE: [CommandHandler('start', start),
                        MessageHandler(Filters.contact, phone),
                        MessageHandler(Filters.text, phone)],

                REG_ADDRESS: [CommandHandler('start', start),
                              MessageHandler(Filters.text, reg_address)],

                PROMO: [CommandHandler('start', start),
                        MessageHandler(Filters.text, promo)],

                CREATED_ORDER: [CommandHandler('start', start),
                                MessageHandler(Filters.text, created_orders)],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
