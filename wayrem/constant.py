# # For Server
from django.core.files.storage import FileSystemStorage
WAYREM_ADMIN_BASE_URL = "https://admin-stg.wayrem.com/"
WAYREM_SUPPLIER_BASE_URL = "https://supplier-stg.wayrem.com/"

# For Local
# WAYREM_ADMIN_BASE_URL = "http://127.0.0.1:8000/"
# WAYREM_SUPPLIER_BASE_URL = "http://127.0.0.1:8001/wayrem_supplier/"
upload_storage = FileSystemStorage(
    location='/opt/app/wayrem-admin-backend/media/common_folder')
