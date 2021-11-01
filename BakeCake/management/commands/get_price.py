from BakeCake.models import Price, Order, Profile


def get_price(chat_id):

    cake = Price.objects.all()
    for ingredient in cake:
        price = {
            'Один уровень': ingredient.level_1,
            'Два уровня': ingredient.level_2,
            'Три уровня': ingredient.level_3,
            'Квадрат': ingredient.square,
            'Круг': ingredient.circle,
            'Прямоугольник': ingredient.rectangle,
            'Без топпинга': ingredient.without_topping,
            'Белый соус': ingredient.white_syrup,
            'Карамельный сироп': ingredient.caramel_syrup,
            'Кленовый сироп': ingredient.maple_syrup,
            'Клубничный сироп': ingredient.strawberry_syrup,
            'Черничный сироп': ingredient.blueberry_syrup,
            'Молочный шоколад': ingredient.milk_chocolate,
            'Ежевика': ingredient.blackberry,
            'Малина': ingredient.raspberry,
            'Голубика': ingredient.blueberry,
            'Клубника': ingredient.strawberry,
            'Фисташки': ingredient.pistachios,
            'Безе': ingredient.meringue,
            'Фундук': ingredient.hazelnuts,
            'Пекан': ingredient.pecan,
            'Маршмеллоу': ingredient.marshmallow,
            'Марципан': ingredient.marzipan,
            'Надпись': ingredient.title,
        }
        return show_order(price,chat_id)


def show_order(price,chat_id):
    profile = Profile.objects.get(
        external_id=chat_id,
    )
    orders = Order.objects.filter(profile=profile).order_by('created_at')
    print(orders)
    all_orders = []
    for order in orders:
        order_number = Order.objects.get(pk=order.pk)
        if order_number.order_status:
            status = 'Статус заказа: торт у вас'
        elif order_number.order_status == False:
            status = 'Статус заказа: торт в пути'
        else:
            status = 'Статус заказа: готовим ваш торт'
        if not order_number.berries == 'Не выбрано':
            berries = f'\nЯгоды:\n{order_number.berries} (+{price[order_number.berries]}р.)'
        else:
            berries = ' '
        if not order_number.decor == 'Не выбрано':
            decor = f'\nДекор:\n{order_number.decor} (+{price[order_number.decor]})р.)'
        else:
            decor = ' '
        if not order_number.title == 'Не выбрано':
            title = f'\nНадпись:\n{order_number.title} (+{price[order_number.title]})р.)'
        else:
            title = ' '
        single_order = f'''
{order}
{status}
Количество уровней:
{order_number.number_levels} (+{price[order_number.number_levels]}р.)
Форма:
{order_number.form} (+{price[order_number.form]}р.)
Топпинг:
{order_number.topping} (+{price[order_number.topping]}р.){berries}{decor}{title}
'''
        all_orders.append(single_order)
        # print(order)
        # order_number = Order.objects.get(pk=order.pk)
        # if order_number.order_status == None:
        #     print('Статус заказа: готовим ваш торт')
        # if order_number.order_status == False:
        #     print('Статус заказа: торт в пути')
        # if order_number.order_status == True:
        #     print('Статус заказа: торт у вас')
        # print('Количество уровней:')
        # print(f'{order_number.number_levels} (+{price[order_number.number_levels]})р')
        # print('Форма:')
        # print(f'{order_number.form} (+{price[order_number.form]})р')
        # print(f'Топпинг:')
        # print(f'{order_number.topping} (+{price[order_number.topping]})р')
        # if not order_number.berries == 'Не выбрано':
        #     print('Ягоды:')
        #     print(f'{order_number.berries} (+{price[order_number.berries]})р')
        # if not order_number.decor == 'Не выбрано':
        #     print('Декор:')
        #     print(f'{order_number.decor} (+{price[order_number.decor]})р')
        # if not order_number.title == 'Не выбрано':
        #     print('Надпись:')
        #     print(f'{order_number.title} (+{price[order_number.title]})р')

    return all_orders

