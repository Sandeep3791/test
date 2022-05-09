from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
from wayrem.constant import upload_storage
import uuid


po_status = (
    ('accept', 'Accept'),
    ('deny', 'Deny'),
    ('cancel', 'Cancel'),
    ('waiting for approval', 'Waiting for approval'),
    ('delivered', 'Delivered'),
)


class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    po_id = models.UUIDField(default=uuid.uuid4)
    po_name = models.CharField(max_length=250, null=True)
    product_name = models.ForeignKey(
        'Products', on_delete=models.SET_NULL, null=True)
    supplier_product = models.ForeignKey(
        'SupplierProducts', on_delete=models.SET_NULL, null=True)
    product_qty = models.IntegerField(null=False, default=1)
    supplier_name = models.ForeignKey(
        'Supplier', on_delete=models.CASCADE, null=False)
    available = models.BooleanField(default=True)
    reason = models.TextField(default=None, null=True)
    status = models.CharField(
        max_length=35, choices=po_status, default='waiting for approval', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'po_master'


class PO_log(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    po = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'po_logs'
