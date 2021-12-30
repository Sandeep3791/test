from django.db import models
from .models import *
import random

def create_new_ref_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(1000000000, 9999999999)
        if not Orders.objects.filter(ref_number=unique_ref):
            not_unique = False
    return str(unique_ref)


class Orders(models.Model):
    ref_number = models.CharField(unique=True, max_length=100,editable=False)
    customer = models.ForeignKey('wayrem_admin.Customer', models.DO_NOTHING)
    status = models.ForeignKey('OrderStatus', models.DO_NOTHING, db_column='status')
    sub_total = models.FloatField()
    item_discount = models.FloatField()
    item_margin = models.FloatField()
    tax = models.FloatField()
    shipping = models.FloatField()
    total = models.FloatField()
    promo = models.CharField(max_length=50, blank=True, null=True)
    discount = models.FloatField()
    grand_total = models.FloatField()
    order_ship_name = models.CharField(max_length=100)
    order_ship_address = models.CharField(max_length=100)
    order_billing_name = models.CharField(max_length=100)
    order_billing_address = models.CharField(max_length=100)
    order_city = models.CharField(max_length=50)
    order_country = models.CharField(max_length=50)
    order_phone = models.CharField(max_length=20)
    order_email = models.CharField(max_length=100)
    order_date = models.DateTimeField()
    order_shipped = models.IntegerField()
    order_tracking_number = models.CharField(max_length=80, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ref_number

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'orders'

class OrderStatus(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_collation='utf8mb4_unicode_ci')

    def __str__(self):
        return self.name
        
    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_status'


class OrderDetails(models.Model):
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    sku = models.CharField(max_length=100)
    product = models.ForeignKey('wayrem_admin.Products', models.DO_NOTHING)
    product_name = models.CharField(max_length=250)
    price = models.FloatField()
    item_margin = models.FloatField()
    discount = models.FloatField()
    quantity = models.SmallIntegerField()

    def __str__(self):
        return self.sku

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_details'


class OrderDeliveryLogs(models.Model):
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    order_status = models.ForeignKey('OrderStatus', models.DO_NOTHING)
    order_status_details = models.TextField(blank=True, null=True)
    log_date = models.DateTimeField()
    user = models.ForeignKey('wayrem_admin.User', models.DO_NOTHING)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_delivery_logs'


class OrderTransactions(models.Model):
    user_id = models.IntegerField()
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    code = models.CharField(max_length=100)
    order_type = models.SmallIntegerField()
    mode = models.SmallIntegerField()
    status = models.SmallIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_transactions'
        