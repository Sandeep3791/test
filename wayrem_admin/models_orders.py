from django.db import models
from .models import *
import random


def create_new_ref_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(1000, 999999)
        if not Orders.objects.filter(ref_number=unique_ref):
            not_unique = False
    return str(unique_ref)


class Orders(models.Model):
    ref_number = models.CharField(unique=True, max_length=100, editable=False)
    customer = models.ForeignKey('wayrem_admin.Customer', models.DO_NOTHING)
    delivery_status = models.ForeignKey(
        'StatusMaster', models.DO_NOTHING, db_column='delivery_status', related_name='delivery_status_id')
    status = models.ForeignKey(
        'StatusMaster', models.DO_NOTHING, db_column='status', related_name='status_id')
    sub_total = models.FloatField()
    item_discount = models.FloatField()
    item_margin = models.FloatField()
    tax = models.FloatField()
    tax_vat = models.FloatField()
    shipping = models.FloatField()
    total = models.FloatField()
    promo = models.CharField(max_length=50, blank=True, null=True)
    discount = models.FloatField()
    grand_total = models.FloatField()
    order_ship_name = models.CharField(max_length=100)
    order_ship_address = models.CharField(max_length=100)

    order_ship_building_name = models.CharField(max_length=100)
    order_ship_landmark = models.CharField(max_length=100)
    order_ship_region = models.CharField(max_length=100)
    order_ship_latitude = models.CharField(max_length=100)
    order_ship_longitude = models.CharField(max_length=100)

    order_billing_name = models.CharField(max_length=100)
    order_billing_address = models.CharField(max_length=100)
    order_city = models.CharField(max_length=50)
    order_country = models.CharField(max_length=50)
    order_phone = models.CharField(max_length=20)
    order_email = models.CharField(max_length=100)
    order_date = models.DateTimeField()
    order_shipped = models.IntegerField()
    order_tracking_number = models.CharField(
        max_length=80, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    order_shipping_response = models.TextField(blank=True, null=True)
    order_type = models.ForeignKey(
        'StatusMaster', models.DO_NOTHING, db_column='order_type', blank=True, null=True)
    delivery_charge = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.ref_number

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'orders'


class StateCode(models.Model):
    state = models.CharField(max_length=255, blank=True, null=True)
    loginext_code = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'state_code'


class StatusMaster(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_collation='utf8mb4_unicode_ci')
    description = models.CharField(max_length=255, blank=True, null=True)
    status_color = models.CharField(max_length=50)
    status_type = models.SmallIntegerField()
    sort_order = models.SmallIntegerField()
    customer_view = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'status_master'


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
    order_status = models.ForeignKey('StatusMaster', models.DO_NOTHING)
    order_status_details = models.TextField(blank=True, null=True)
    log_date = models.DateTimeField()
    user = models.ForeignKey('wayrem_admin.User', models.DO_NOTHING)
    customer_view = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_delivery_logs'


class OrderTransactions(models.Model):
    user_id = models.IntegerField()
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    invoices_id = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=100)
    order_type = models.SmallIntegerField()
    payment_mode = models.ForeignKey(
        'StatusMaster', models.DO_NOTHING, db_column='payment_mode_id', related_name='ae_payment_mode')
    payment_status = models.ForeignKey(
        'StatusMaster', models.DO_NOTHING, db_column='payment_status_id', related_name='ae_payment_status')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    bank_payment_image = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_transactions'


class ShippingLoginextNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    notification_type = models.CharField(max_length=255, blank=True, null=True)
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    shipment_request_no = models.CharField(
        max_length=255, blank=True, null=True)
    shipment_request_dispatch_date = models.CharField(
        max_length=255, blank=True, null=True)
    shipment_request_type = models.CharField(
        max_length=255, blank=True, null=True)
    service_type = models.CharField(max_length=255, blank=True, null=True)
    pickup_account_code = models.CharField(
        max_length=255, blank=True, null=True)
    pickup_address_id = models.CharField(max_length=255, blank=True, null=True)
    deliver_account_code = models.CharField(
        max_length=255, blank=True, null=True)
    deliver_address_id = models.CharField(
        max_length=255, blank=True, null=True)
    return_account_code = models.CharField(
        max_length=255, blank=True, null=True)
    return_address_id = models.CharField(max_length=255, blank=True, null=True)
    client_code = models.CharField(max_length=255, blank=True, null=True)
    orderrequest_timestamp = models.DateTimeField(blank=True, null=True)
    order_no = models.CharField(max_length=255, blank=True, null=True)
    awb_number = models.CharField(max_length=255, blank=True, null=True)
    order_state = models.CharField(max_length=255, blank=True, null=True)
    order_leg = models.CharField(max_length=255, blank=True, null=True)

    scan_status = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    scan_time = models.DateTimeField(blank=True, null=True)

    delivery_medium_name = models.CharField(
        max_length=255, blank=True, null=True)
    delivery_medium_user_name = models.CharField(
        max_length=255, blank=True, null=True)
    carrier_name = models.CharField(max_length=255, blank=True, null=True)
    carrier_branch_name = models.CharField(
        max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    trip_name = models.CharField(max_length=255, blank=True, null=True)
    acceptedorder_timestamp = models.DateTimeField(blank=True, null=True)
    track_url = models.CharField(max_length=255, blank=True, null=True)
    pickup_end_date = models.DateTimeField(blank=True, null=True)
    delivery_end_date = models.DateTimeField(blank=True, null=True)
    reason_of_rejection = models.CharField(
        max_length=100, blank=True, null=True)
    rejectedorder_timestamp = models.DateTimeField(blank=True, null=True)

    cancellation_time = models.DateTimeField(blank=True, null=True)
    customer_code = models.CharField(max_length=100, blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True)
    reason_cd = models.CharField(max_length=100, blank=True, null=True)
    cancelled_by = models.CharField(max_length=100, blank=True, null=True)
    is_cancel_occur_after_pickup_fl = models.IntegerField(
        blank=True, null=True)
    delivery_medium_reference_id = models.CharField(
        max_length=100, blank=True, null=True)
    location_type = models.CharField(max_length=100, blank=True, null=True)
    check_in_time = models.CharField(max_length=100, blank=True, null=True)
    checkin_latitude = models.CharField(max_length=100, blank=True, null=True)
    checkin_longitude = models.CharField(max_length=100, blank=True, null=True)
    parent_order_no = models.CharField(max_length=100, blank=True, null=True)

    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    order_status = models.CharField(max_length=100, blank=True, null=True)
    customer_comment = models.CharField(max_length=100, blank=True, null=True)
    customer_rating = models.CharField(max_length=100, blank=True, null=True)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    cash_amount = models.CharField(max_length=100, blank=True, null=True)
    delivery_location_type = models.CharField(
        max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    actual_cash_amount = models.CharField(
        max_length=100, blank=True, null=True)
    payment_mode = models.CharField(max_length=100, blank=True, null=True)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    payment_sub_type = models.CharField(max_length=100, blank=True, null=True)
    client_id = models.CharField(max_length=100, blank=True, null=True)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)

    vehicle_number = models.CharField(max_length=200, blank=True, null=True)
    trip_reference_id = models.CharField(max_length=200, blank=True, null=True)
    number_of_items = models.CharField(max_length=200, blank=True, null=True)
    package_weight = models.CharField(max_length=200, blank=True, null=True)
    package_volume = models.CharField(max_length=200, blank=True, null=True)
    origin_addr = models.CharField(max_length=200, blank=True, null=True)
    destination_addr = models.CharField(max_length=200, blank=True, null=True)
    shipment_order_type_cd = models.CharField(
        max_length=200, blank=True, null=True)
    client_node_name = models.CharField(max_length=200, blank=True, null=True)
    client_node_cd = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    delivery_type = models.CharField(max_length=200, blank=True, null=True)
    shipment_notes = models.CharField(max_length=200, blank=True, null=True)
    assignment_method = models.CharField(max_length=200, blank=True, null=True)

    apartment = models.CharField(max_length=50, blank=True, null=True)
    street_name = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=50, blank=True, null=True)
    customer_email_address = models.CharField(
        max_length=50, blank=True, null=True)
    customer_phone_number = models.CharField(
        max_length=50, blank=True, null=True)

    start_time_window = models.DateTimeField(blank=True, null=True)
    end_time_window = models.DateTimeField(blank=True, null=True)
    calculated_start_dt = models.DateTimeField(blank=True, null=True)
    calculated_end_dt = models.DateTimeField(blank=True, null=True)
    shipment_crate_mapping = models.TextField(blank=True, null=True)
    ordercreate_timestamp = models.DateTimeField(blank=True, null=True)
    ordercreate_timestamp = models.DateTimeField(blank=True, null=True)
    picked_up_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'shipping_loginext_notification'


class OrderLoginextShipment(models.Model):
    customer = models.ForeignKey('wayrem_admin.Customer', models.DO_NOTHING)
    customer_account_code = models.CharField(
        max_length=255, blank=True, null=True)
    customer_reference_id = models.CharField(
        max_length=255, blank=True, null=True)
    create_customer_response = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'order_loginext_shipment'


class CustomerNotification(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey('wayrem_admin.Orders', models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    message = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'customer_notification'
