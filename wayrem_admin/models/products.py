from django.template.defaultfilters import default, slugify
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem.constant import upload_storage
import random
import os

status = (("Active", "Active"), ("Inactive", "Inactive"))

UNIT = (
    ('absolute', 'abs'),
    ('%', '%'),
)

DIS_ABS_PERCENT = (
    ('Absolute', 'Abs'),
    ('%', '%'),
)


def get_file_path(obj, fname):
    fname = fname.split('.')[-1]
    num = random.randint(111, 999)
    if obj.SKU:
        fname = '{}_{}.{}'.format(obj.SKU, num, fname)
    else:
        pass
    return os.path.join(
        'products',
        obj.SKU,
        fname,
    )


class Products(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    SKU = models.CharField(max_length=255, null=True, blank=False, unique=True)
    category = models.ManyToManyField('Categories', null=True)
    # product_code = models.CharField(max_length=255, null=True)
    meta_key = models.TextField(null=True, blank=True)
    feature_product = models.BooleanField(default=True)
    publish = models.BooleanField(default=False)
    date_of_mfg = models.DateField(blank=True, null=True)
    date_of_exp = models.DateField(blank=True, null=True)
    mfr_name = models.CharField(max_length=100, null=True, blank=True)
    supplier = models.ManyToManyField('Supplier', null=True, blank=True)
    dis_abs_percent = models.CharField(
        max_length=20, choices=DIS_ABS_PERCENT, null=True, blank=False)
    description = models.TextField(null=True, blank=True)
    warehouse = models.ForeignKey('Warehouse', models.DO_NOTHING, null=True)
    quantity = models.CharField(max_length=100, null=True, default=1)
    quantity_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_quantity_unit')
    weight = models.CharField(blank=True, null=True, max_length=255)
    weight_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_weight_unit')
    price = models.CharField(null=True, max_length=100)
    discount = models.CharField(max_length=50, null=True, blank=True)
    package_count = models.CharField(
        max_length=50, null=True, blank=True, default=1)
    wayrem_margin = models.CharField(max_length=100, blank=True, null=True)
    margin_unit = models.CharField(
        max_length=20, choices=DIS_ABS_PERCENT, null=True, blank=True)
    primary_image = models.ImageField(
        upload_to=get_file_path, storage=upload_storage, default='product.jpg', null=True)
    gs1 = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inventory_starting = models.SmallIntegerField(default=0)
    inventory_received = models.SmallIntegerField(default=0)
    inventory_shipped = models.SmallIntegerField(default=0)
    inventory_cancelled = models.SmallIntegerField(default=0)
    inventory_onhand = models.SmallIntegerField(default=0)
    outofstock_threshold = models.SmallIntegerField(
        default=0, null=True, blank=True,)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " (SKU: " + self.SKU + ")"

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'products_master'


def get_product_images_path(obj, fname):
    fname = fname.split('.')[-1]
    num = random.randint(111, 999)
    if obj.product.SKU:
        fname = '{}_{}.{}'.format(obj.product.SKU, num, fname)
    else:
        pass
    return os.path.join(
        'products',
        obj.product.SKU,
        fname,
    )


def get_image_filename(instance, filename):
    title = instance.products.name
    slug = slugify(title)
    return "product_images/%s-%s" % (slug, filename)


class Images(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, default=None)
    image = models.FileField(
        upload_to=get_product_images_path, storage=upload_storage, verbose_name='product_mage')

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'product_images'


class ProductIngredients(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.IntegerField()
    ingredient = models.ForeignKey(
        'Ingredients', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.CharField(max_length=25, default=1, blank=True)
    unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'product_ingredients'


class GS1ProductFields(models.Model):
    ai_code = models.CharField(max_length=255, null=True)
    product_field = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'gs1_product_fields'
