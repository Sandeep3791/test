from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *


class Unit(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    unit_name = models.CharField(max_length=15, null=False, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.unit_name

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'unit_master'
