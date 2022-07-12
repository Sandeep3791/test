from django.urls import path
from wayrem_admin import views

urlpatterns = [
        path('<int:id>', views.WalletList.as_view(), name='walletlistcreate'),
]
