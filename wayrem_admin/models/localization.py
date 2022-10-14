from django.db import models
from wayrem_admin.utils.constants import *
from django.db import connection

class Language(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    iso_code = models.CharField(max_length=100)
    status = models.IntegerField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'language'

class LocalizationMobileSettings(models.Model):
    localization_key = models.CharField(max_length=500)
    lang_en = models.TextField()
    lang_ar = models.TextField()

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))
            
    class Meta:
        app_label = "wayrem_admin"
        db_table = 'localization_mobile_settings'