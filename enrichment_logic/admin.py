from django.contrib import admin
from .models import Category, Merchant, Keyword, Transaction

admin.site.register(Category)
admin.site.register(Merchant)
admin.site.register(Keyword)
admin.site.register(Transaction)
