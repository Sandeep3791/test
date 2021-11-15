from django.urls import path, include
from wayrem_admin import views

app_name = 'wayrem_admin'

urlpatterns = [
    path('auth/', include('wayrem_admin.urls.auth')),
    path('account/', include('wayrem_admin.urls.account')),
    path('category/', include('wayrem_admin.urls.category')),
    path('home/', include('wayrem_admin.urls.home')),
    path('ingredients/', include('wayrem_admin.urls.ingredients')),
    path('product/', include('wayrem_admin.urls.product')),
    path('purchase_order/', include('wayrem_admin.urls.purchase_order')),
    path('roles/', include('wayrem_admin.urls.roles')),
    path('supplier/', include('wayrem_admin.urls.supplier')),
    path('', views.RootUrlView.as_view(), name='root')
]
