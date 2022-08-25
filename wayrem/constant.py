# # For Server
from django.core.files.storage import FileSystemStorage
WAYREM_ADMIN_BASE_URL = "https://admin-uat.wayrem.com/"
WAYREM_SUPPLIER_BASE_URL = "https://supplier-uat.wayrem.com/"
DOCUMENT_URL = "https://admin-uat.wayrem.com/media/common_folder/"

# For Local
# WAYREM_ADMIN_BASE_URL = "http://127.0.0.1:8000/"
# WAYREM_SUPPLIER_BASE_URL = "http://127.0.0.1:8001/wayrem_supplier/"
upload_storage = FileSystemStorage(
    location='/opt/app/wayrem-admin-backend/media/common_folder')
