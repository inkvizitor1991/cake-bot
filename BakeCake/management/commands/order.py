import re
import phonenumbers

price = {'Один уровень': 'Один уровень (+400р)',
         'Два уровня': 'Два уровня (+750р)',
         'Три уровня': 'Три уровня (+1100р)', 'Квадрат': 'Квадрат (+600)',
         'Круг': 'Круг (+400)', 'Прямоугольник': 'Прямоугольник (+1000)',
         'Без топпинга': 'Без топпинга (+0)',
         'Белый соус': 'Белый соус (+200)',
         'Карамельный сироп': 'Карамельный сироп (+180)',
         'Кленовый сироп': 'Кленовый сироп (+200)',
         'Клубничный сироп': 'Клубничный сироп (+300)',
         'Черничный сироп': 'Черничный сироп (+350)',
         'Молочный шоколад': 'Молочный шоколад (+200)',
         'Ежевика': 'Ежевика (+400)', 'Клубника': 'Клубника (+500)',
         'Малина': 'Малина (+300)', 'Голубика': 'Голубика (+450)',
         'Пропустить': 'Не выбрано', 'Маршмеллоу': 'Маршмеллоу (+200)',
         'Фисташки': 'Фисташки (+300)', 'Безе': 'Безе (+400)',
         'Фундук': 'Фундук (+350)', 'Пекан': 'Пекан (+300)', }


def get_order_parser(order_text, promo_code, bc_speed):
    price = re.findall(r'\d+', order_text)
    int_price = []
    for num in price:
        int_price.append(int(num))
    order_price = sum(int_price)
    if promo_code == 'BakeCake200':
        promo_code = 200
    else:
        promo_code = 0
    if bc_speed:
        speed = f'\n+20% за скорость {int((order_price - promo_code) * 1.2)}p.'
    else:
        speed = ''
    total_price = f'''
    Промокод: -{promo_code}p
    Цена заказа: {order_price - promo_code}p.{speed}
    '''
    return total_price


def get_order_text(new_order):
    total_levels, bc_form, bc_topping, bc_berries, bc_decor, bc_inscription, bc_comment, bc_address, bc_delivery_date, bc_delivery_time, promo_code, bc_speed = new_order
    if not bc_inscription == 'Пропустить':
        bc_inscription = f'{bc_inscription} (+500)'
    else:
        bc_inscription = 'Не выбрано'
    if bc_comment == 'Пропустить':
        bc_comment = 'Не выбрано'
    order_text = f'''
    Ваш заказ:
    Количество уровней:
    {price[total_levels]}
    Форма:
    {price[bc_form]}
    Топпинг:
    {price[bc_topping]}
    Ягоды:
    {price[bc_berries]}
    Декор:
    {price[bc_decor]}
    Надпись:
    {bc_inscription}
    '''
    order_price = get_order_parser(order_text, promo_code, bc_speed)
    delivery = f'''
    Доставка:
    Адрес:
    {bc_address}
    День доставки:
    {bc_delivery_date}
    Время доставки:
    {bc_delivery_time}
    Комментарий к заказу:
    {bc_comment}
    '''
    return order_text, delivery, order_price


def test_phone(phonenumber):
    number = phonenumbers.parse(phonenumber, 'RU')
    if phonenumbers.is_valid_number(number):
        phone = phonenumbers.format_number(
            number,
            phonenumbers.PhoneNumberFormat.E164
        )
        return phone
    else:
        return False
