from BakeCake.models import Profile, Order

#chat_id = 495816173
#chat_id = update.message.chat_id
def get_adress(chat_id):
    profile = Profile.objects.get(external_id=chat_id)
    orders = Order.objects.filter(profile=profile).order_by('-created_at')[0]
    return orders.address