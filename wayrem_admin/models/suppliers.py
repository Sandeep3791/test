from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
from wayrem.constant import upload_storage

deliverable = (
    ('1', 'within 1 day'),
    ('2', 'within 2 day'),
    ('3', 'within 3 day'),
    ('4', 'within 4 day'),
    ('5', 'within 5 day'),
)

invoice_status = (
    ('released', 'Released'),
    ('complete', 'Complete'),
    ('cancel', 'Cancel'),
)


class Supplier(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    company_phone_no = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    company_email = models.EmailField(blank=False, unique=True, null=True)
    registration_no = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    from_time = models.TimeField(blank=True, null=True)
    to_time = models.TimeField(blank=True, null=True)
    # from_time = models.DateTimeField(auto_now=True)
    # to_time = models.DateTimeField(auto_now=True)
    contact_person_name = models.CharField(max_length=255, null=True)
    contact_phone_no = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=200)
    contact = models.BigIntegerField(null=True)
    logo = models.ImageField(
        upload_to='supplier/', storage=upload_storage,  null=True, default='supplier/default.jpg')
    address = models.TextField(null=True, blank=True)
    delivery_incharge = models.CharField(max_length=500, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=False, null=True)
    is_active = models.BooleanField(default=True)
    category_name = models.ManyToManyField('Categories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'supplier_master'


class SupplierProducts(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    supplier_id = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey(
        'Products', on_delete=models.CASCADE, db_column='product_id', null=True, blank=True)
    SKU = models.CharField(max_length=250, null=True, blank=True)
    product_name = models.CharField(max_length=500, null=True, blank=True)
    quantity = models.IntegerField(null=True, default=1)
    price = models.CharField(null=True, max_length=255)
    available = models.BooleanField(default=True)
    deliverable_days = models.CharField(max_length=20,
                                        choices=deliverable, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'product_suppliers'


class OtpDetails(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'supplier_otp'


class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'invoice_master'


class BestProductsSupplier(models.Model):
    product_id = models.IntegerField()
    supplier_id = models.IntegerField()
    lowest_price = models.CharField(max_length=255)
    lowest_delivery_time = models.CharField(max_length=255)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'best_products_supplier'


class Notification(models.Model):
    message = models.TextField()
    status = models.BooleanField(default=False)
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'notifications'
