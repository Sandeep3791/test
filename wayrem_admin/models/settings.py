from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *

TYPE = (
    ('text', 'Text'),
    ('textarea', 'Textarea'),
)


class Settings(models.Model):
    key = models.CharField(max_length=191, null=False, unique=True)
    display_name = models.CharField(max_length=191, null=False, unique=True)
    value = models.TextField()
    details = models.TextField()
    type = models.CharField(max_length=40, choices=TYPE,
                            null=True, default="text")
    order = models.IntegerField(null=False, default="1")

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'settings'


class EmailTemplateModel(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255)
    to_email = models.CharField(max_length=255,)
    subject = models.CharField(max_length=255,)
    message_format = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(null=False, default=1)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'email_template'


class StaticPages(models.Model):
    page_title = models.CharField(max_length=255, null=True)
    slug = models.SlugField(max_length=255, null=True)
    description = models.TextField(null=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'static_pages'
