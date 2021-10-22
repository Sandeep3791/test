from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'contact', 'role']


@admin.register(Roles)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'role']


@admin.register(Categories)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category_image', 'description']

@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredients_name']