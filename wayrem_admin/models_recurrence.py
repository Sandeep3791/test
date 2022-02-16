from django.db import models
from .models import *


class RecurrentType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    value = models.SmallIntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'recurrent_type'


class RecurrenceGrocery(models.Model):
    customer_id = models.IntegerField(blank=True, null=True)
    grocery = models.ForeignKey(
        'GroceryMaster', models.DO_NOTHING, blank=True, null=True)
    recurrenttype = models.ForeignKey(
        'RecurrentType', models.DO_NOTHING, db_column='recurrenttype', blank=True, null=True)
    recurrence_startdate = models.CharField(max_length=255)
    recurrence_nextdate = models.CharField(max_length=255)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'recurrence_grocery'


class GroceryMaster(models.Model):
    grocery_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    customer = models.ForeignKey(
        'wayrem_admin.Customer', models.DO_NOTHING, blank=True, null=True)
    address = models.ForeignKey(
        'wayrem_admin.CustomerAddresses', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'grocery_master'


class GroceryProducts(models.Model):
    grocery = models.ForeignKey(
        'GroceryMaster', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey('wayrem_admin.Products', models.DO_NOTHING)
    product_qty = models.IntegerField(blank=True, null=True)
    recurrence_nextdate = models.CharField(
        max_length=255, blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'grocery_products'


class ForecastJobtype(models.Model):
    id = models.SmallAutoField(primary_key=True)
    no_of_days = models.SmallIntegerField()
    status = models.IntegerField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'forecast_jobtype'


class ForecastProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    forecast_jobtype_id = models.SmallIntegerField()
    product_id = models.IntegerField()
    stock = models.SmallIntegerField()
    forecast_quantity = models.SmallIntegerField()
    needed_stock_purchase = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'forecast_product'
