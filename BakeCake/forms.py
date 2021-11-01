from django import forms
from .models import Profile, Order, Price

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'external_id',
            'name',
            'first_name',
            'last_name',
            'phone'

        )
        widgets = {
            'name':forms.TextInput,
            'external_id':forms.TextInput,
            'first_name':forms.TextInput,
            'last_name':forms.TextInput,
            'phone':forms.TextInput

        }
class MessageForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'id',
            'number_levels',
            'form',
            'topping',
            'berries',
            'decor',
            'title',
            'comment',
            'address',
            'delivery_date',
            'delivery_time'
        )
        widgets = {
            'id':forms.TextInput,
            'number_levels':forms.TextInput,
            'form':forms.TextInput,
            'topping':forms.TextInput,
            'berries':forms.TextInput,
            'decor':forms.TextInput,
            'title':forms.TextInput,
            'comment':forms.TextInput,
            'address':forms.TextInput,
            'delivery_date':forms.TextInput,
            'delivery_time':forms.TextInput

        }

