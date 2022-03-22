
from django.db import models
from datetime import datetime
import uuid
from django.core.files.storage import FileSystemStorage
from wayrem_admin.models.StaticModels import Products, SupplierProducts, Supplier


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


    
#------------------supplier_ghj models-----------------------------------------------------------------------------


class Invoice_ghj(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "ghj. Invoice"
        db_table = 'ghj_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_ghj(models.Model):
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
        verbose_name_plural = "ghj. PurchaseOrder"
        db_table = 'ghj_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_asds models-----------------------------------------------------------------------------


class Invoice_asds(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "asds. Invoice"
        db_table = 'asds_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_asds(models.Model):
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
        verbose_name_plural = "asds. PurchaseOrder"
        db_table = 'asds_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_frwes models-----------------------------------------------------------------------------


class Invoice_frwes(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "frwes. Invoice"
        db_table = 'frwes_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_frwes(models.Model):
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
        verbose_name_plural = "frwes. PurchaseOrder"
        db_table = 'frwes_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_Supp models-----------------------------------------------------------------------------


class Invoice_Supp(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Supp. Invoice"
        db_table = 'Supp_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_Supp(models.Model):
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
        verbose_name_plural = "Supp. PurchaseOrder"
        db_table = 'Supp_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_vij models-----------------------------------------------------------------------------


class Invoice_vij(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "vij. Invoice"
        db_table = 'vij_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_vij(models.Model):
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
        verbose_name_plural = "vij. PurchaseOrder"
        db_table = 'vij_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_ran models-----------------------------------------------------------------------------


class Invoice_ran(models.Model):
    invoice_id = models.AutoField(primary_key=True, unique=True)
    invoice_no = models.CharField(max_length=250, null=True)
    po_name = models.CharField(max_length=250, null=True)
    ro_name = models.CharField(max_length=250, null=True)
    file = models.FileField(upload_to='invoices/', storage=upload_storage,
                            null=True)
    supplier_name = models.CharField(max_length=250, null=True)    
    status = models.CharField(
        max_length=35, choices=invoice_status, default='released', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "ran. Invoice"
        db_table = 'ran_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_ran(models.Model):
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
        verbose_name_plural = "ran. PurchaseOrder"
        db_table = 'ran_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        
#------------------supplier_kjl models-----------------------------------------------------------------------------


class Invoice_kjl(models.Model):
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
        verbose_name_plural = "kjl. Invoice"
        db_table = 'kjl_Invoice'
    def __str__(self):
        return str(self.invoice_no)
    

class PurchaseOrder_kjl(models.Model):
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
        verbose_name_plural = "kjl. PurchaseOrder"
        db_table = 'kjl_purchase_order'
    def __str__(self):
        return str(self.po_id)


#--------------------------------------------------------------------------------------------------------------


        