from django.db import models

CHOICES = (
    (None, 'Готовим ваш торт'),
    (False, 'Торт в пути'),
    (True, 'Торт у вас')
)


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в сети',
        unique=True
    )
    name = models.CharField(
        'Псевдоним',
        max_length=10
    )
    first_name = models.CharField(
        'Имя пользователя',
        blank=True,
        max_length=10
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        null=True,
        blank=True,
        max_length=10
    )
    phone = models.CharField(
        'Телефон пользователя',
        blank=True,
        max_length=20,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Order(models.Model):
    profile = models.ForeignKey(
        'Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )

    created_at = models.DateTimeField(
        'Время получения',
        auto_now_add=True
    )
    order_status = models.BooleanField(
        'Статус заказа',
        choices=CHOICES,
        null=True)
    number_levels = models.CharField(
        'Количество уровней', blank=True,
        max_length=20
    )
    form = models.CharField('Форма', blank=True, max_length=20)
    topping = models.CharField('Топпинг', blank=True, max_length=20)
    berries = models.CharField('Ягоды', blank=True, max_length=20)
    decor = models.CharField('Декор', blank=True, max_length=20)
    title = models.TextField('Надпись', blank=True, max_length=30)
    comment = models.TextField(
        'Комментарий к заказу', blank=True,
        max_length=200
    )
    address = models.CharField('Адрес доставки', blank=True, max_length=50)
    delivery_date = models.CharField(
        'Дата доставки', blank=True,
        max_length=20
    )
    delivery_time = models.CharField(
        'Время доставки', blank=True,
        max_length=20
    )

    def __str__(self):
        return f'Заказ {self.pk} от {self.profile}'

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'


class Price(models.Model):
    level_1 = models.IntegerField('Один уровень', default=400)
    level_2 = models.IntegerField('Два уровня', default=750)
    level_3 = models.IntegerField('Три уровня', default=1100)
    square = models.IntegerField('Квадрат', default=600)
    circle = models.IntegerField('Круг', default=400)
    rectangle = models.IntegerField('Прямоугольник', default=1000)
    without_topping = models.IntegerField('Без топпинга', default=0)
    white_syrup = models.IntegerField('Белый соус', default=200)
    caramel_syrup = models.IntegerField('Карамельный сироп', default=180)
    maple_syrup = models.IntegerField('Кленовый сироп', default=200)
    strawberry_syrup = models.IntegerField('Клубничный сироп', default=300)
    blueberry_syrup = models.IntegerField('Черничный сироп', default=350)
    milk_chocolate = models.IntegerField('Молочный шоколад', default=200)
    blackberry = models.IntegerField('Ежевика', default=400)
    raspberry = models.IntegerField('Малина', default=300)
    blueberry = models.IntegerField('Голубика', default=450)
    strawberry = models.IntegerField('Клубника ', default=500)
    pistachios = models.IntegerField('Фисташки', default=300)
    meringue = models.IntegerField('Безе', default=400)
    hazelnuts = models.IntegerField('Фундук', default=350)
    pecan = models.IntegerField('Пекан', default=300)
    marshmallow = models.IntegerField('Маршмеллоу', default=200)
    marzipan = models.IntegerField('Марципан', default=280)
    title = models.IntegerField('Надпись', default=500)

    class Meta:
        verbose_name = 'Цены'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return 'Торт'
