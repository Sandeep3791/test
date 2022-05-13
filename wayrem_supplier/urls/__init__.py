from django.urls import path, include
from wayrem_supplier import views
from wayrem_supplier.views.auth import SupplierAddApi, SupplierAddMigrationsApi
from wayrem_supplier.AlterModelsScript import AlterModelsCreate


app_name = 'wayrem_supplier'

urlpatterns = [
    path('auth/', include('wayrem_supplier.urls.auth')),
    path('invoice/', include('wayrem_supplier.urls.invoice')),
    path('product/', include('wayrem_supplier.urls.product')),
    path('purchase_order/', include('wayrem_supplier.urls.purchase_order')),
    path('', views.RootUrlView.as_view(), name='root'),
    path('api/create/user/models', SupplierAddApi, name='create_models'),
    path('api/create/user/models/migrate',
         SupplierAddMigrationsApi, name='create_models_migrate'),
    path('AlterModelsCreateSupplier',
         AlterModelsCreate, name="AlterModelsCreate"),


]
