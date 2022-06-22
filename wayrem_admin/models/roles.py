from django.db import models
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField
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
    ('Static Pages Add', 'Static Pages Add'), ('Static Pages Edit', 'Static Pages Edit'), ('Static Pages Delete',
                                                                                           'Static Pages Delete'), ('Static Pages View', 'Inventory View'),
)

status = (("Active", "Active"), ("Inactive", "Inactive"))


class Roles(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    role = models.CharField(max_length=50, unique=True)
    permission = MultiSelectField(
        choices=roles_options, max_length=15000, default="Stats")
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wayrem_roles'

    def __str__(self):
        return self.role
