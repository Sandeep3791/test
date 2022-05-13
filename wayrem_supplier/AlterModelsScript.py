from http.client import HTTPResponse
# from aiohttp import payload
from django.core.files import File
from django.core.management import call_command
import requests, json
from supplier.settings import BASE_DIR
import os
from wayrem_supplier.models import Supplier
from django.http import HttpResponse, JsonResponse, request, HttpResponseRedirect
from rest_framework.decorators import api_view


@api_view(['POST'])
def AlterModelsCreate(request):
    key = request.data
    if key["key"] == "mnbvcjhgdsndckvnifhvkmvgwer":
        models = CreateModels()
        return HttpResponse(models)
        
    else:
        return HttpResponse("Enter valied key")


def CreateModels():

    old_name = os.path.join(BASE_DIR, "wayrem_supplier/models/SupplierModels.py")
    new_name = os.path.join(BASE_DIR, "wayrem_supplier/models/New_SupplierModels.txt")
    # new_name = r"./models/New_Models.txt"

    if os.path.isfile(new_name):
        os.remove(new_name)

    os.rename(old_name, new_name)
    file = old_name
    open(file, 'a').close()


    w = open(old_name, 'a')
    w.write("""

from django.db import models
from datetime import datetime
import uuid
from django.core.files.storage import FileSystemStorage
from wayrem_supplier.models.StaticModels import Products, SupplierProducts, Supplier


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

    """)
    supplierData = Supplier.objects.all().order_by("-pk")
    for suppliers in supplierData:
        w.write("""
#------------------supplier_{0} models-----------------------------------------------------------------------------


class Invoice_{0}(models.Model):
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
        verbose_name_plural = "{0}. Invoice"
        db_table = '{0}_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_{0}(models.Model):
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
        verbose_name_plural = "{0}. PurchaseOrder"
        db_table = '{0}_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        """.format(suppliers.username))

    w.close
    # call_command('makemigrations')
    return "models created successfully"











