from django.urls import path, include
from wayrem_admin import views

app_name = 'wayrem_admin'

urlpatterns = [
    path('auth/', include('wayrem_admin.urls.auth')),
    path('account/', include('wayrem_admin.urls.account')),
    path('category/', include('wayrem_admin.urls.category')),
    path('credits/', include('wayrem_admin.urls.credits')),
    path('customer/', include('wayrem_admin.urls.customer')),
    path('home/', include('wayrem_admin.urls.home')),
    path('ingredient/', include('wayrem_admin.urls.ingredients')),
    path('products/', include('wayrem_admin.urls.product')),
    path('purchase_order/', include('wayrem_admin.urls.purchase_order')),
    path('roles/', include('wayrem_admin.urls.roles')),
    path('supplier/', include('wayrem_admin.urls.supplier')),
    path('settings/', include('wayrem_admin.urls.setting')),
    path('invoices/', include('wayrem_admin.urls.invoice')),
    path('email-templates/', include('wayrem_admin.urls.emailtemplates')),
    path('warehouses/', include('wayrem_admin.urls.warehouse')),
    path('inventories/', include('wayrem_admin.urls.inventory')),
    path('orders/', include('wayrem_admin.urls.order')),
    path('wallet/', include('wayrem_admin.urls.wallet')),

    path('shipping-rates/', include('wayrem_admin.urls.shippingrates')),
    path('loginext/', include('wayrem_admin.loginext.urls')),
    path('home/pages/', include('wayrem_admin.urls.static_pages')),
    path('banks/', include('wayrem_admin.urls.banks')),
    path('available-stock/', include('wayrem_admin.urls.available_stock')),
    path('', views.RootUrlView.as_view(), name='root')
]
