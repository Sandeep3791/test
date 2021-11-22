from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'contact', 'role']


@admin.register(Roles)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'role']


@admin.register(Categories)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category_image', 'description']


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredients_name']


@admin.register(SupplierProducts)
class SuProductAdmin(admin.ModelAdmin):
    list_display = ['id', "product_name", "SKU"]


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', "product_name", "SKU"]
