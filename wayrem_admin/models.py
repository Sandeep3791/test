# from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid
from multiselectfield import MultiSelectField
from django.template.defaultfilters import slugify


# Create your models here.
roles_options = (
    ('Roles Add', 'Roles Add'), ('Roles Edit', 'Roles Edit'), ('Roles Delete',
                                                               'Roles Delete'), ('Roles View', 'Roles View'),
    ('User Add', 'User Add'), ('User Edit', 'User Edit'), ('User Delete',
                                                           'User Delete'), ('User View', 'User View'),
    ('Categories Add', 'Categories Add'), ('Categories Edit', 'Categories Edit'), (
        'Categories Delete', 'Categories Delete'), ('Categories View', 'Categories View'),
    ('Products Add', 'Products Add'), ('Products Edit', 'Products Edit'), ('Products Delete',
                                                                           'Products Delete'), ('Products View', 'Products View'),
    ('Supplier Add', 'Supplier Add'), ('Supplier Edit', 'Supplier Edit'), (
        'Supplier Delete', 'Supplier Delete'), ('Supplier View', 'Supplier View'),
    ('Purchase Order Add', 'Purchase Order Add'), ('Purchase Order Edit', 'Purchase Order Edit'), (
        'Purchase Order Delete', 'Purchase Order Delete'), ('Purchase Order View', 'Purchase Order View'),
    ('Customer Profile Add', 'Customer Profile Add'), ('Customer Profile Edit', 'Customer Profile Edit'), (
        'Customer Profile Delete', 'Customer Profile Delete'), ('Customer Profile View', 'Customer Profile View'),
    ('Customer Order Add', 'Customer Order Add'), ('Customer Order Edit', 'Customer Order Edit'), (
        'Customer Order Delete', 'Customer Order Delete'), ('Customer Order View', 'Customer Order View'),
    ('Finance Add', 'Finance Add'), ('Finance Edit', 'Finance Edit'), ('Finance Delete',
                                                                       'Finance Delete'), ('Finance View', 'Finance View'),
    ('Reports Add', 'Reports Add'), ('Reports Edit', 'Reports Edit'), ('Reports Delete',
                                                                       'Reports Delete'), ('Reports View', 'Reports View'),
)

status = (("Active", "Active"), ("Inactive", "Inactive"))


class Roles(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    role = models.CharField(max_length=50, unique=True)
    permission = MultiSelectField(choices=roles_options, default="Stats")
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wayrem_roles'

    def __str__(self):
        return self.role


class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(_('email address'), unique=True)
    contact = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    role = models.ForeignKey(
        Roles, on_delete=models.DO_NOTHING, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='M', null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users_master'


class Otp(models.Model):
    email = models.EmailField()
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'otp'


class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=35, unique=True)
    category_image = models.ImageField(
        upload_to='assets/category/', blank=False, null=True)
    tag = models.TextField(null=True, blank=True)
    margin = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories_master'


class SubCategories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=35, unique=True)
    tag = models.TextField(null=True, blank=True)
    margin = models.IntegerField()
    image = models.ImageField(
        upload_to='assets/subcategory/', blank=False, null=True)
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'subcategories_master'


class Supplier(models.Model):
    id = models.UUIDField(default=uuid.uuid1, primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=200)
    contact = models.BigIntegerField(null=True)
    logo = models.ImageField(upload_to='images/', null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    delivery_incharge = models.CharField(max_length=500, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=False, null=True)
    is_active = models.BooleanField(default=True)
    category_name = models.ManyToManyField('Categories', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = 'supplier_master'


class Ingredients(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
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


DIS_ABS_PERCENT = (
    ('(Absolute ', 'Abs'),
    ('%', '%'),
)
UNIT_CHOICES = (
    ('GRAM', 'gm'),
    ('KILO-GRAM', 'kg'),
    ('MILLI-LITRE', 'ml'),
    ('LITRE', 'ltr'),
)


class Products(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    SKU = models.CharField(max_length=255, null=True, blank=False)
    category = models.ManyToManyField('Categories', null=True)
    product_code = models.CharField(max_length=255, null=True)
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
    quantity = models.IntegerField(null=True, default=1)
    weight = models.IntegerField(null=True)
    unit = models.CharField(
        max_length=20, choices=UNIT_CHOICES, null=True, blank=False)
    price = models.DecimalField(null=True, max_digits=12, decimal_places=2)
    discount = models.CharField(max_length=50, null=True, blank=False)
    package_count = models.IntegerField(null=True)
    wayrem_margin = models.IntegerField(null=True)
    margin_unit = models.CharField(
        max_length=20, choices=DIS_ABS_PERCENT, null=True, blank=False)
    primary_image = models.ImageField(upload_to='product/images/', null=True)
    gs1 = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products_master'


def get_image_filename(instance, filename):
    title = instance.products.name
    slug = slugify(title)
    return "product_images/%s-%s" % (slug, filename)


class Images(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, default=None)
    image = models.FileField(upload_to="product/images/",
                             verbose_name='product_mage')


class Unit(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    unit_name = models.CharField(max_length=15, null=False, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.unit_name


class ProductIngredients(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    product = models.UUIDField()
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.CharField(max_length=25, default=1, blank=True)
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True)


class PurchaseOrder(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    po_id = models.UUIDField(default=uuid.uuid4)
    po_name = models.CharField(max_length=250, null=True)
    product_name = models.ForeignKey(
        Products, on_delete=models.CASCADE, null=True)
    product_qty = models.IntegerField(null=False, default=1)
    supplier_name = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=False)
    po_status = (
        ('accept', 'Accept'),
        ('deny', 'Deny'),
        ('cancel', 'Cancel'),
        ('in progress', 'In Progress'),
        ('delivered', 'Delivered'),
    )
    status = models.CharField(
        max_length=35, choices=po_status, default='in progress', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'po_master'


class OtpDetails(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=255)
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supplier_otp'


class SupplierProducts(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    supplier_id = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True)
    SKU = models.CharField(max_length=250, null=True, blank=True)
    product_name = models.CharField(max_length=500, null=True, blank=True)
    quantity = models.IntegerField(null=True, default=1)
    price = models.DecimalField(null=True, max_digits=12, decimal_places=2)
    available = models.BooleanField(default=True)
    deliverable = (
        ('1', 'within 1 day'),
        ('2', 'within 2 day'),
        ('3', 'within 3 day'),
        ('4', 'within 4 day'),
        ('5', 'within 5 day'),
    )
    deliverable_days = models.CharField(max_length=20,
                                        choices=deliverable, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_suppliers'


class Customer(models.Model):
    id = models.CharField(max_length=255, default=uuid.uuid4, primary_key=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=12, null=True, unique=True)
    city = models.CharField(max_length=500, null=True)
    country = models.CharField(max_length=500, null=True)
    address = models.CharField(max_length=500, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers_master'

# 6281073150012
# 6281035000034
# 69321494000400


class Invoice(models.Model):
    invoice_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='images/', null=True)
    supplier_name = models.CharField(max_length=250, null=True)
    invoice_status = (
        ('released', 'Released'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel'),
    )
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice_master'


class Settings(models.Model):
    key = models.CharField(max_length=191, null=False, unique=True)
    display_name = models.CharField(max_length=191, null=False, unique=True)
    value = models.TextField()
    details = models.TextField()
    type = models.CharField(max_length=191, null=False)
    order = models.IntegerField(null=False, default="1")

    class Meta:
        db_table = 'settings'
