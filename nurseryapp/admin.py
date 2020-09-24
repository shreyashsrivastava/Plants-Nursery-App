from django.contrib import admin
from .models import Plants, CustomUser, Order, OrderItem, ShippingAddress
# Register your models here.

admin.site.register(Plants)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)