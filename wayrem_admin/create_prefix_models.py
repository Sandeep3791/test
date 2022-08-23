from django.core.files import File
from django.core.management import call_command
import requests
import json
from wayrem.settings import BASE_DIR
import os
from wayrem import constant


def create_supplier_models_cluster(username):
    with open(os.path.join(BASE_DIR, "wayrem_admin/models/SupplierModels.py"), 'r') as f2:
        data = f2.read()
    try:
        w = open(os.path.join(
            BASE_DIR, "wayrem_admin/models/SupplierModels.py"), 'a')
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
    unit_price = models.CharField(max_length=250, null=True)
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


        """.format(username))
        w.close
        try:
            url = constant.WAYREM_SUPPLIER_BASE_URL + "api/create/user/models"
            payload = {'username': username}
            headers = {
                'Content-Type': 'application/json',
                'Cookie': 'csrftoken=X3RzQAn8PQbOGQLRHFEPBRkg3PMqDQttqe1VMXe1iGHhtvQ6hHmfz8VK18BriYNV'
            }
            body = json.dumps(payload)
            response = requests.request(
                "POST", url, headers=headers, data=body)

        except Exception as e:
            print(e)
            return e
        return True
    except:
        w = open(os.path.join(
            BASE_DIR, "wayrem_admin/models/SupplierModels.py"), 'w')
        testfile = File(w)
        testfile.write(str(data))
        testfile.close
        w.close
        return "not created"


def runtime_migrations():
    call_command('makemigrations')
    call_command('migrate')
    url = constant.WAYREM_SUPPLIER_BASE_URL + 'api/create/user/models/migrate'
    response = requests.request('GET', url)
    response = response.json()
    print(response)
    return True
