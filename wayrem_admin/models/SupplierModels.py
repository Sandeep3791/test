
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

