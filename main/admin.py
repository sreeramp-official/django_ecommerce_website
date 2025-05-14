from django.contrib import admin
from .models import Product, CustomUser, Order, OrderItem

admin.site.register(Product)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)
