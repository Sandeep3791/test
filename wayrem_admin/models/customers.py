from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
from wayrem.constant import upload_storage


customer_status = (
    ('waiting for approval', 'Waiting for Approval'),
    ('active', 'Active'),
    ('inactive', 'Inactive')
)


class Customer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    business_type = models.ForeignKey(
        'BusinessType', models.DO_NOTHING, null=True)
    business_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=12, null=True, unique=True)
    # city = models.CharField(max_length=500, null=True)
    # country = models.CharField(max_length=500, null=True)
    # address = models.TextField(null=True)
    profile_pic = models.CharField(max_length=500, null=True)
    about = models.TextField(null=True)
    reject_reason = models.CharField(max_length=500, null=True)
    status = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=100, choices=customer_status, null=True, default='waiting for approval')
    registration_number = models.BigIntegerField(null=True)
    tax_number = models.BigIntegerField(null=True)
    registration_docs_path = models.CharField(max_length=255, null=True)
    tax_docs_path = models.CharField(max_length=255, null=True)
    marrof_docs_path = models.CharField(max_length=255, null=True)
    # billing_name = models.CharField(max_length=255, null=True)
    # billing_address = models.TextField(null=True)
    delivery_house_no_building_name = models.CharField(
        max_length=255, null=True)
    delivery_road_name_Area = models.CharField(max_length=255, null=True)
    delivery_landmark = models.CharField(max_length=255, null=True)
    delivery_country = models.CharField(max_length=255, null=True)
    delivery_region = models.CharField(max_length=255, null=True)
    delivery_town_city = models.CharField(max_length=255, null=True)
    billing_house_no_building_name = models.CharField(
        max_length=255, null=True)
    billing_road_name_Area = models.CharField(max_length=255, null=True)
    billing_landmark = models.CharField(max_length=255, null=True)
    billing_country = models.CharField(max_length=255, null=True)
    billing_region = models.CharField(max_length=255, null=True)
    billing_town_city = models.CharField(max_length=255, null=True)
    deliveryAddress_latitude = models.CharField(max_length=255, null=True)
    deliveryAddress_longitude = models.CharField(max_length=255, null=True)
    billlingAddress_Latitude = models.CharField(max_length=255, null=True)
    billingAddress_longitude = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customers_master'


class CustomerAddresses(models.Model):
    customer = models.ForeignKey(
        Customer, models.DO_NOTHING, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.BigIntegerField(blank=True, null=True)
    house_no_building_name = models.CharField(
        max_length=255, blank=True, null=True)
    # Field name made lowercase.
    road_name_area = models.CharField(
        db_column='road_name_Area', max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    town_city = models.CharField(max_length=255, blank=True, null=True)
    # Field name made lowercase.
    deliveryaddress_latitude = models.CharField(
        db_column='deliveryAddress_latitude', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    deliveryaddress_longitude = models.CharField(
        db_column='deliveryAddress_longitude', max_length=255, blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customer_addresses'


class CustomerDevice(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255, null=True)
    device_type = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customer_device'


class BusinessType(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    business_type = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'business_type'


class CustomerNotification(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    customer = models.ForeignKey(
        'wayrem_admin.Customer', on_delete=models.CASCADE)
    order = models.ForeignKey('wayrem_admin.Orders', models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    message = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customer_notification'


class PaymentTransaction(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    order_id = models.IntegerField(null=True, blank=True)
    transaction_id = models.TextField(null=True, blank=True)
    checkout_id = models.TextField(null=True, blank=True)
    response_body = models.TextField(null=True, blank=True)
    payment_type = models.CharField(max_length=255, null=True, blank=True)
    payment_brand = models.CharField(max_length=255, null=True, blank=True)
    amount = models.CharField(max_length=255, blank=True, default=0.00)
    status = models.CharField(max_length=255, blank=True, default="PAID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'payment_transactions'


class CardDetails(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    registration_id = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=50, null=True, blank=True)
    expiry_month = models.CharField(max_length=50, null=True, blank=True)
    expiry_year = models.CharField(max_length=50, null=True, blank=True)
    card_holder = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.CharField(max_length=255, null=True, blank=True)
    card_body = models.TextField(null=True, blank=True)
    card_brand = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customer_cards'


class CreditSettings(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    credit_amount = models.IntegerField()
    time_period = models.IntegerField()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'credit_settings'


# class CreditManagement(models.Model):
#     id = models.AutoField(primary_key=True, unique=True)
#     customer = models.ForeignKey("Customer", models.CASCADE)
#     credit = models.ForeignKey("CreditSettings", models.CASCADE)
#     used = models.FloatField()
#     available = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     class Meta:
#         db_table = 'credit_management'
