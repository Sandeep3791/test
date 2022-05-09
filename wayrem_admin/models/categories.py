from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
from wayrem.constant import upload_storage
UNIT = (
    ('absolute', 'abs'),
    ('%', '%'),
)


class Categories(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=35, unique=True)
    image = models.ImageField(
        upload_to="category/",  default='category/category.jpg', storage=upload_storage, blank=False, null=True)
    tag = models.TextField(null=True, blank=True)
    parent = models.CharField(max_length=35,  null=True)
    margin = models.IntegerField()
    unit = models.CharField(
        max_length=20, choices=UNIT, null=True, default="%")
    is_parent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + " - " + str(self.margin) + " " + self.unit

    class Meta:
        db_table = 'categories_master'
