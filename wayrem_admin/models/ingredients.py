from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *


status = (("Active", "Active"), ("Inactive", "Inactive"))


class Ingredients(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ingredients_name = models.CharField(
        max_length=100, unique=True, null=True, blank=False)
    ingredients_status = models.CharField(
        max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ingredients_name

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'ingredient_master'
