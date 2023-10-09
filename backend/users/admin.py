from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username',
                    'first_name', 'last_name', 'is_staff')
    list_filter = ('email', 'first_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribing')
    list_filter = ('subscriber',)
    search_fields = ('subscriber', 'subscribing')
