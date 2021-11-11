# from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid
from multiselectfield import MultiSelectField


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
    role = models.CharField(max_length=50)
    permission = MultiSelectField(choices=roles_options, default="Stats")
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'wayrem_roles'

    def __str__(self):
        return self.role


class CustomUser(AbstractUser):
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
        db_table = 'custom_user'


class Otp(models.Model):
    email = models.EmailField()
    otp = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'otp'


class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    category_image = models.ImageField(
        upload_to='images/', blank=True, null=True)
    description = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'


class SupplierRegister(models.Model):
    id = models.UUIDField(default=uuid.uuid1, primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=200)
    contact = models.BigIntegerField(null=True)
    logo = models.ImageField(upload_to='images/', null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    delivery_incharge = models.CharField(max_length=500, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    category_name = models.ManyToManyField('Categories', null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'supplier_master'


class Ingredients(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    ingredients_name = models.CharField(
        max_length=100, unique=True, null=True, blank=False)
    ingredients_status = models.CharField(
        max_length=10, choices=status, default='Active')

    def __str__(self):
        return self.ingredients_name

    class Meta:
        db_table = 'ingredients'


class Products(models.Model):
    # ----------------------------------First slide model------------------------------------------------------------
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    SKU = models.CharField(max_length=255, null=True, blank=True)
    # product_category = models.ForeignKey(Categories, on_delete=models.CASCADE,null=True,blank=True)
    product_category = models.ManyToManyField('Categories', null=True)
    product_code = models.CharField(max_length=255, null=True)
    product_meta_key = models.CharField(max_length=250)
    feature_product = models.BooleanField(default=True)
    product_deliverable = models.BooleanField(default=True)
    date_of_mfg = models.DateField()
    date_of_exp = models.DateField()
    mfr_name = models.CharField(max_length=100, null=True, blank=True)
    # supplier_name = models.ForeignKey(SupplierRegister, on_delete=models.CASCADE)
    supplier_name = models.ManyToManyField('SupplierRegister', null=True)
    DIS_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    dis_abs_percent = models.CharField(max_length=20,
                                       choices=DIS_ABS_PERCENT, null=True, blank=True)

    # -------------------------------Second slide model------------------------------------------------------------
    image1 = models.ImageField(upload_to='images/', null=True)
    image2 = models.ImageField(upload_to='images/', null=True)
    image3 = models.ImageField(upload_to='images/', null=True)
    image4 = models.ImageField(upload_to='images/', null=True)
    image5 = models.ImageField(upload_to='images/', null=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255)
    ingredients1 = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name='Products1', null=True, blank=True)
    ingredients2 = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name='Products2', null=True, blank=True)
    ingredients3 = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name='Products3', null=True, blank=True)
    ingredients4 = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, related_name='Products4', null=True, blank=True)
    calories1 = models.CharField(
        max_length=25, null=True, blank=True)
    calories2 = models.CharField(
        max_length=25, null=True, blank=True)
    calories3 = models.CharField(
        max_length=25, null=True, blank=True)
    calories4 = models.CharField(
        max_length=25, null=True, blank=True)
    nutrition = models.CharField(max_length=20, null=True, blank=True)
    product_qty = models.IntegerField(null=True, default=1)
    # ---------------------------------Third slide model-----------------------------------------------------------
    product_weight = models.IntegerField(null=True)
    UNIT_CHOICES = (
        ('GRAM', 'gm'),
        ('KILO-GRAM', 'kg'),
        ('MILLI-LITRE', 'ml'),
        ('LITRE', 'ltr'),
    )
    unit = models.CharField(max_length=20,
                            choices=UNIT_CHOICES, null=True, blank=True)
    # price = models.FloatField(null=True, max_length=255, decimal_places=2)
    price = models.DecimalField(null=True, max_digits=12, decimal_places=2)
    discount = models.CharField(max_length=50, null=True, blank=True)
    package_count = models.IntegerField(null=True)
    # --------------------------------Fourth slide model--------------------------------------------------------------------
    wayrem_margin = models.IntegerField(null=True)
    WAYREM_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    wayrem_abs_percent = models.CharField(max_length=20,
                                          choices=DIS_ABS_PERCENT, null=True, blank=True)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'product_master'


class PurchaseOrder(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    po_id = models.UUIDField(default=uuid.uuid4)
    po_name = models.CharField(max_length=250, null=True)
    product_name = models.ForeignKey(
        Products, on_delete=models.CASCADE, null=True)
    product_qty = models.IntegerField(null=False, default=1)
    supplier_name = models.ForeignKey(
        SupplierRegister, on_delete=models.CASCADE, null=False)
    po_status = (
        ('accept', 'Accept'),
        ('deny', 'Deny'),
        ('cancel', 'Cancel'),
        ('in progress', 'In Progress'),
        ('delivered', 'Delivered'),
    )
    status = models.CharField(
        max_length=35, choices=po_status, default='in progress', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'po_master'


# 6281073150012
# 6281035000034
# 69321494000400
