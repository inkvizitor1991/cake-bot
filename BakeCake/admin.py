from django.contrib import admin
from .forms import ProfileForm, MessageForm
from .models import Order, Profile,Price



class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['first_name','last_name']
    list_display = (
        'id','external_id', 'name','first_name','last_name', 'phone'

    )
    form = ProfileForm

class OrderAdmin(admin.ModelAdmin):
    list_filter = ['order_status']
    list_display = ('id','profile','order_status','created_at')
    list_editable = ['order_status']
    form = MessageForm

class PriceAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Количество уровней', {
        'fields': ('level_1', 'level_2','level_3')}),
        ('Форма', {
            'fields': ('square','circle','rectangle')}),
        ('Топпинг', {
            'fields': ('without_topping','white_syrup','caramel_syrup',
                       'maple_syrup','strawberry_syrup',
                       'blueberry_syrup','milk_chocolate'
                       )}),

        ('Ягоды', {
            'fields': ('blackberry','raspberry','blueberry','strawberry')}),
        ('Декор', {
            'fields': ('pistachios','meringue','hazelnuts','pecan',
                        'marshmallow','marzipan'
                       )}),
        ('Надпись', {
            'fields': ('title',)}),

    )
    #form = PriceForm






admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Price,PriceAdmin)
