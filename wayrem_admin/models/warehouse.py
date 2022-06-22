from django.db import models
from django.utils.translation import ugettext_lazy as _


status = (("Active", "Active"), ("Inactive", "Inactive"))


class Warehouse(models.Model):
    code_name = models.CharField(max_length=255)
    branch_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=100, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code_name

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'warehouse'


class ShippingRates(models.Model):
    from_dest = models.FloatField()
    to_dest = models.FloatField()
    price = models.FloatField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'shipping_rates'
