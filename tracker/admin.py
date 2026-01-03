from django.contrib import admin

from .models import Account, Card, Category, Expense, Message, WhatsAppUser

admin.site.register(WhatsAppUser)
admin.site.register(Account)
admin.site.register(Card)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Message)
