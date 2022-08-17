from django.db import models
from datetime import datetime
import uuid
from django.core.files.storage import FileSystemStorage


status = (("Active", "Active"), ("Inactive", "Inactive"))

UNIT = (
    ('absolute ', 'abs'),
    ('%', '%'),
)

DIS_ABS_PERCENT = (
    ('Absolute ', 'Abs'),
    ('%', '%'),
)

UNIT_CHOICES = (
    ('GRAM', 'gm'),
    ('KILO-GRAM', 'kg'),
    ('MILLI-LITRE', 'ml'),
    ('LITRE', 'ltr'),
)

deliverable = (
    ('1', 'Within 1 days'),
    ('2', 'Within 2 days'),
    ('3', 'Within 3 days'),
    ('4', 'Within 4 days'),
    ('5', 'Within 5 days'),
)

po_status = (
    ('accept', 'Accept'),
    ('deny', 'Deny'),
    ('cancel', 'Cancel'),
    ('waiting for approval', 'Waiting for approval'),
    ('delivered', 'Delivered'),
)

invoice_status = (
    ('released', 'Released'),
    ('complete', 'Complete'),
    ('cancel', 'Cancel'),
)

TYPE = (
    ('text', 'Text'),
    ('textarea', 'Textarea'),
)

upload_storage = FileSystemStorage(
    location='/opt/app/wayrem-admin-backend/media/common_folder')

# upload_storage = FileSystemStorage(
#     location='/home/fealty/Desktop/Supplier/wayrem-admin-backend/media/common_folder')


class Supplier(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    company_phone_no = models.CharField(
        max_length=12, null=True, unique=True, blank=True)
    company_email = models.EmailField(blank=True, unique=True, null=True)
    registration_no = models.CharField(
        max_length=12, null=True, unique=True, blank=True)
    from_time = models.TimeField(blank=True, null=True)
    to_time = models.TimeField(blank=True, null=True)
    # from_time = models.DateTimeField(auto_now=True)
    # to_time = models.DateTimeField(auto_now=True)
    contact_person_name = models.CharField(
        max_length=255, null=True, blank=True)
    contact_phone_no = models.CharField(
        max_length=12, null=True, unique=True, blank=True)
    email = models.EmailField(blank=True, unique=True, null=True)
    password = models.CharField(max_length=200)
    contact = models.BigIntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='supplier/', storage=upload_storage,
                             null=True, blank=True, default='supplier/default.jpg')
    address = models.TextField(null=True, blank=True)
    delivery_incharge = models.CharField(max_length=500, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    category_name = models.ManyToManyField('Categories', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = 'supplier_master'


class Categories(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=35, unique=True)
    image = models.ImageField(
        upload_to='', storage=upload_storage, blank=False, null=True)
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


class OtpDetails(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supplier_otp'


class Ingredients(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ingredients_name = models.CharField(
        max_length=100, unique=True, null=True, blank=False)
    ingredients_status = models.CharField(
        max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ingredients_name

    class Meta:
        db_table = 'ingredient_master'


class Unit(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    unit_name = models.CharField(max_length=15, null=False, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.unit_name

    class Meta:
        db_table = 'unit_master'


class Products(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    SKU = models.CharField(max_length=255, null=True, blank=False, unique=True)
    category = models.ManyToManyField('Categories', null=True)
    # product_code = models.CharField(max_length=255, null=True)
    meta_key = models.TextField()
    feature_product = models.BooleanField(default=True)
    publish = models.BooleanField(default=False)
    date_of_mfg = models.DateField(null=True)
    date_of_exp = models.DateField(null=True)
    mfr_name = models.CharField(max_length=100, null=True, blank=False)
    supplier = models.ManyToManyField('Supplier', null=True)
    dis_abs_percent = models.CharField(
        max_length=20, choices=DIS_ABS_PERCENT, null=True, blank=False)
    description = models.TextField()
    quantity = models.CharField(max_length=100, null=True, default=1)
    quantity_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_quantity_unit')
    weight = models.CharField(null=True, max_length=255)
    weight_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_weight_unit')
    price = models.CharField(null=True, max_length=100)
    discount = models.CharField(max_length=50, null=True, blank=False)
    package_count = models.CharField(
        max_length=50, null=True, blank=True, default=1)
    wayrem_margin = models.CharField(max_length=100, null=True)
    margin_unit = models.CharField(
        max_length=20, choices=DIS_ABS_PERCENT, null=True, blank=False)
    primary_image = models.ImageField(
        upload_to='', storage=upload_storage, null=True)
    gs1 = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products_master'


class SupplierProducts(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    supplier_id = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, null=True)
    SKU = models.CharField(max_length=250, null=True, blank=True)
    product_name = models.CharField(max_length=500, null=True, blank=True)
    quantity = models.IntegerField(null=True, default=1)
    price = models.CharField(null=True, max_length=255)
    available = models.BooleanField(default=True)
    deliverable_days = models.CharField(max_length=20,
                                        choices=deliverable, null=True, blank=True, default='2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_suppliers'


class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    po_id = models.UUIDField(default=uuid.uuid4)
    po_name = models.CharField(max_length=250, null=True)
    product_name = models.ForeignKey(
        Products, on_delete=models.SET_NULL, null=True)
    supplier_product = models.ForeignKey(
        SupplierProducts, on_delete=models.SET_NULL, null=True)
    product_qty = models.IntegerField(null=False, default=1)
    supplier_name = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=False)
    available = models.BooleanField(default=True)
    reason = models.TextField(default=None, null=True)
    status = models.CharField(
        max_length=35, choices=po_status, default='waiting for approval', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'po_master'


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
        db_table = 'invoice_master'


class BestProductsSupplier(models.Model):
    product_id = models.IntegerField()
    supplier_id = models.IntegerField()
    lowest_price = models.CharField(max_length=255)
    lowest_delivery_time = models.CharField(max_length=255)

    class Meta:
        db_table = 'best_products_supplier'


class Notification(models.Model):
    message = models.TextField()
    status = models.BooleanField(default=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'


class Settings(models.Model):
    key = models.CharField(max_length=191, null=False, unique=True)
    display_name = models.CharField(max_length=191, null=False, unique=True)
    value = models.TextField()
    details = models.TextField()
    type = models.CharField(max_length=40, choices=TYPE,
                            null=True, default="text")
    order = models.IntegerField(null=False, default="1")

    class Meta:
        db_table = 'settings'


# class PO_log(models.Model):
#     id = models.AutoField(primary_key=True, unique=True)
#     po = models.ForeignKey(
#         PurchaseOrder, on_delete=models.CASCADE, null=True, blank=True)
#     status = models.CharField(max_length=255, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'po_logs'

class PO_log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    po = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'po_logs'


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
