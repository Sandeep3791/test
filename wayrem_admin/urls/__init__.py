from django.urls import path, include
from wayrem_admin import views

app_name = 'wayrem_admin'

urlpatterns = [
    path('auth/', include('wayrem_admin.urls.auth')),
    path('account/', include('wayrem_admin.urls.account')),
    path('category/', include('wayrem_admin.urls.category')),
    path('subcategory/', include('wayrem_admin.urls.subcategory')),
    path('customer/', include('wayrem_admin.urls.customer')),
    path('home/', include('wayrem_admin.urls.home')),
    path('ingredient/', include('wayrem_admin.urls.ingredients')),
    path('products/', include('wayrem_admin.urls.product')),
    path('purchase_order/', include('wayrem_admin.urls.purchase_order')),
    path('roles/', include('wayrem_admin.urls.roles')),
    path('supplier/', include('wayrem_admin.urls.supplier')),
    path('settings/', include('wayrem_admin.urls.setting')),
    path('invoices/', include('wayrem_admin.urls.invoice')),
    path('', views.RootUrlView.as_view(), name='root')
]
