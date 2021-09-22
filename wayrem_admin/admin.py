from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'contact', 'role']


@admin.register(Roles)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'role']
