# from typing_extensions import Required
# from models_orders import Orders
from django.core.validators import MinValueValidator
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.base import Model
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid
from multiselectfield import MultiSelectField
from django.template.defaultfilters import default, slugify
from django.db.models import Sum
from wayrem_admin.utils.constants import *
#from models_orders import Orders,OrderDetails

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
        'Customer Order Delete', 'Customer Order Delete'), ('Customer Order View', 'Customer Order View'), ('Customer Invoice Order', 'Customer Invoice Order'),

    ('Finance Add', 'Finance Add'), ('Finance Edit', 'Finance Edit'), ('Finance Delete',
                                                                       'Finance Delete'), ('Finance View', 'Finance View'),
    ('Reports Add', 'Reports Add'), ('Reports Edit', 'Reports Edit'), ('Reports Delete',
                                                                       'Reports Delete'), ('Reports View', 'Reports View'),
    ('Email Template Add', 'Email Template Add'), ('Email Template Edit', 'Email Template Edit'), ('Email Template Delete',
                                                                                                   'Email Template Delete'), ('Email Template View', 'Email Template View'),
    ('Warehouse Add', 'Warehouse Add'), ('Warehouse Edit', 'Warehouse Edit'), (
        'Warehouse Delete', 'Warehouse Delete'), ('Warehouse View', 'Warehouse View'),
    ('Inventory Add', 'Inventory Add'), ('Inventory Edit', 'Inventory Edit'), ('Inventory Delete',
                                                                               'Inventory Delete'), ('Inventory View', 'Inventory View'),
)

status = (("Active", "Active"), ("Inactive", "Inactive"))

UNIT = (
    ('absolute', 'abs'),
    ('%', '%'),
)

upload_storage = FileSystemStorage(
    location='/opt/app/wayrem-admin-backend/media/common_folder')
# /opt/app/wayrem-admin-backend/media/common_folder
# local storage = /home/fealty/Desktop/wayrem_kapil
#
# server storage =  /home/ubuntu/docker_setup/database
# upload_storage = FileSystemStorage(
#     location='/home/fealty')


class Roles(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    role = models.CharField(max_length=50, unique=True)
    permission = MultiSelectField(
        choices=roles_options, max_length=1500, default="Stats")
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wayrem_roles'

    def __str__(self):
        return self.role


class User(AbstractUser):
    id = models.AutoField(primary_key=True, unique=True)
    po_notify = models.BooleanField(default=False, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    contact = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    role = models.ForeignKey(
        Roles, on_delete=models.CASCADE, null=True, blank=True)
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
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=35, unique=True)
    image = models.ImageField(
        upload_to='',  default='category.jpg', storage=upload_storage, blank=False, null=True)
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


class SubCategories(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=35, unique=True)
    tag = models.TextField(null=True, blank=True)
    margin = models.IntegerField()
    image = models.ImageField(
        upload_to='', storage=upload_storage, blank=False, null=True)
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'subcategories_master'


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
        upload_to='', storage=upload_storage,  null=True, default='default.jpg')
    address = models.TextField(null=True, blank=True)
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


DIS_ABS_PERCENT = (
    ('Absolute', 'Abs'),
    ('%', '%'),
)


class Unit(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    unit_name = models.CharField(max_length=15, null=False, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.unit_name

    class Meta:
        db_table = 'unit_master'


class Warehouse(models.Model):
    code_name = models.CharField(max_length=255)
    address = models.TextField()
    status = models.CharField(max_length=100, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code_name

    class Meta:
        db_table = 'warehouse'


class Products(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=False)
    SKU = models.CharField(max_length=255, null=True, blank=False, unique=True)
    category = models.ManyToManyField('Categories', null=True)
    master_category = models.CharField(max_length=100, null=True, blank=True)

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
    warehouse = models.ForeignKey(Warehouse, models.DO_NOTHING, null=True)
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
        upload_to='', storage=upload_storage, default='product.jpg', null=True)
    gs1 = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inventory_starting = models.SmallIntegerField(default=0)
    inventory_received = models.SmallIntegerField(default=0)
    inventory_shipped = models.SmallIntegerField(default=0)
    inventory_cancelled = models.SmallIntegerField(default=0)
    inventory_onhand = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name + " (SKU: " + self.SKU + ")"

    class Meta:
        db_table = 'products_master'


def get_image_filename(instance, filename):
    title = instance.products.name
    slug = slugify(title)
    return "product_images/%s-%s" % (slug, filename)


class Images(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, default=None)
    image = models.FileField(
        upload_to="", storage=upload_storage, verbose_name='product_mage')

    class Meta:
        db_table = 'product_images'


class ProductIngredients(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.IntegerField()
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.CharField(max_length=25, default=1, blank=True)
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'product_ingredients'


class SupplierProducts(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    supplier_id = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True)
    product_id = models.IntegerField()
    SKU = models.CharField(max_length=250, null=True, blank=True)
    product_name = models.CharField(max_length=500, null=True, blank=True)
    quantity = models.IntegerField(null=True, default=1)
    price = models.CharField(null=True, max_length=255)
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
    po_status = (
        ('accept', 'Accept'),
        ('deny', 'Deny'),
        ('cancel', 'Cancel'),
        ('waiting for approval', 'Waiting for approval'),
        ('delivered', 'Delivered'),
    )
    available = models.BooleanField(default=True)
    reason = models.TextField(default=None, null=True)
    status = models.CharField(
        max_length=35, choices=po_status, default='waiting for approval', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'po_master'


class OtpDetails(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supplier_otp'


class Customer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    business_type = models.CharField(max_length=255, null=True)
    business_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=False, unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=12, null=True, unique=True)
    # city = models.CharField(max_length=500, null=True)
    # country = models.CharField(max_length=500, null=True)
    # address = models.TextField(null=True)
    profile_pic = models.CharField(max_length=500, null=True)
    about = models.TextField(null=True)
    status = models.BooleanField(default=True)
    registration_number = models.BigIntegerField(null=True)
    tax_number = models.BigIntegerField(null=True)
    registration_docs_path = models.CharField(max_length=255, null=True)
    tax_docs_path = models.CharField(max_length=255, null=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers_master'


class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='', storage=upload_storage,
                            null=True)
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


TYPE = (
    ('text', 'Text'),
    ('textarea', 'Textarea'),
)


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


class BestProductsSupplier(models.Model):
    product_id = models.IntegerField()
    supplier_id = models.IntegerField()
    lowest_price = models.CharField(max_length=255)
    lowest_delivery_time = models.CharField(max_length=255)

    class Meta:
        db_table = 'best_products_supplier'


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
        db_table = 'email_template'


class Notification(models.Model):
    message = models.TextField()
    status = models.BooleanField(default=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'


class PO_log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    po = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'po_logs'


class InventoryType(models.Model):
    id = models.SmallAutoField(primary_key=True)
    type_name = models.CharField(
        max_length=50, db_collation='utf8mb4_unicode_ci')
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'inventory_type'


class Inventory(models.Model):
    order_status_choices = (('ordered', 'Ordered'),
                            ('shipped', 'Shipped'), ('cancelled', 'Canceled'))
    id = models.BigAutoField(primary_key=True)
    inventory_type = models.ForeignKey('InventoryType', models.DO_NOTHING)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], blank=False, null=False)
    product = models.ForeignKey(
        'Products', on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey('Warehouse', models.DO_NOTHING, null=True)
    po_id = models.IntegerField(blank=True, null=True)
    supplier_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_status = models.CharField(
        max_length=30, blank=True, null=True, choices=order_status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def po_inventory_process(self, po_id):
        po_details = PurchaseOrder.objects.filter(po_id=po_id, available=True)
        for po_detail in po_details:
            po_detail_dict = {'inventory_type_id': 2, 'quantity': po_detail.product_qty, 'product_id': po_detail.product_name.id, 'warehouse_id': po_detail.product_name.warehouse.id,
                              'po_id': po_detail.id, 'supplier_id': po_detail.supplier_product.supplier_id.id, 'order_id': None, 'order_status': None}
            # print(po_detail_dict)
            self.insert_inventory(po_detail_dict)
        return 1

    def order_inventory_process(self, order_id):
        # When we place order inventory process to shipping
        from wayrem_admin.models_orders import Orders, OrderDetails
        orders = Orders.objects.filter(id=order_id).first()
        order_status = orders.status.id
        order_details = OrderDetails.objects.filter(order=order_id)
        if (order_status == ORDER_STATUS_RECEIVED) or (order_status == ORDER_STATUS_Cancelled):

            for order_detail in order_details:
                inventory_dict = {'inventory_type_id': 3, 'quantity': order_detail.quantity, 'product_id': order_detail.product.id,
                                  'warehouse_id': order_detail.product.warehouse.id, 'po_id': None, 'supplier_id': None, 'order_id': order_id, 'order_status': order_status}

                if (order_status == ORDER_STATUS_RECEIVED):
                    inventory_dict['inventory_type_id'] = 3
                    inventory_dict['order_status'] = INVENTORY_ORDER_STATUS_ORDERED
                else:
                    inventory_dict['inventory_type_id'] = 4
                    inventory_dict['order_status'] = INVENTORY_ORDER_STATUS_CANCELLED
                self.insert_inventory(inventory_dict)
        else:
            # update inventory table
            if (order_status == ORDER_STATUS_DELIVERING):
                inventory_lists = Inventory.objects.filter(
                    order_id=order_id, inventory_type_id=3, order_status=INVENTORY_ORDER_STATUS_ORDERED)
                for inv_list in inventory_lists:
                    inv_id = inv_list.id
                    Inventory.objects.filter(id=inv_id).update(
                        order_status=INVENTORY_ORDER_STATUS_SHIPPED)
        return 1

    def insert_inventory(self, inventory_dict):
        try:
            if ('product_id' in inventory_dict) and ('quantity' in inventory_dict) and ('inventory_type_id' in inventory_dict) and ('warehouse_id' in inventory_dict):
                # inventory_dict={'inventory_type_id':1,'quantity':2,'product_id':1,'warehouse_id':1,'po_id':None,'supplier_id':None,'order_id':None,'order_status':None}
                inventory_create = Inventory(**inventory_dict)
                inventory_create.save()
                product_id = inventory_dict['product_id']
                self.update_product_quantity(product_id)
                return True
            else:
                print("missing value")
        except Exception as e:
            print(e)
            return False

    def update_product_quantity(self, product_id):
        try:
            total_quantity = 0
            inventory_starting = 0
            inventory_received = 0
            inventory_shipped = 0
            inventory_cancelled = 0
            product_type = Inventory.objects.annotate(inventory_quantity=Sum('quantity')).values(
                'inventory_type', 'inventory_quantity').filter(product=product_id).order_by('inventory_type_id')
            product_type.query.group_by = [('inventory_type')]
            for quantity_cal in product_type:
                quantity = quantity_cal['inventory_quantity']
                if quantity_cal['inventory_type'] == 3:
                    total_quantity -= quantity
                    inventory_shipped = quantity
                else:
                    total_quantity += quantity
                    if quantity_cal['inventory_type'] == 1:
                        inventory_starting = quantity
                    elif quantity_cal['inventory_type'] == 2:
                        inventory_received = quantity
                    else:
                        inventory_cancelled = quantity
            Products.objects.filter(id=product_id).update(quantity=total_quantity, inventory_starting=inventory_starting, inventory_received=inventory_received,
                                                          inventory_shipped=inventory_shipped, inventory_cancelled=inventory_cancelled, inventory_onhand=total_quantity)
        except:
            print("An exception occurred")

    def update_product_inventory(self):
        product = self.product
        starting_inventory = 0
        received_inventory = 0
        shipped_inventory = 0
        for inventory in Inventory.objects.filter(product=product):
            if inventory.inventory_type == 'Starting':
                starting_inventory += inventory.quantity
            elif inventory.inventory_type == 'Received':
                received_inventory += inventory.quantity
            else:
                shipped_inventory += inventory.quantity

        inventory_onhand = (received_inventory +
                            starting_inventory)-shipped_inventory
        product.inventory_onhand = inventory_onhand if inventory_onhand >= 0 else 0
        product.inventory_received = received_inventory
        product.starting_inventory = starting_inventory
        product.inventory_shipped = shipped_inventory
        product.save()

    class Meta:
        db_table = 'inventory'
