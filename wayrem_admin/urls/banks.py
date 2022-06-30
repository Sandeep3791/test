from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('', views.BanksList.as_view(), name='banklist'),
    path('update/<int:id>', views.BanksUpdated.as_view(), name='updatebank'),
    path('statusupdate/<int:id>/<int:status>',views.BankUpdateInACView.as_view(),name='statusupdate'),
    path('view/<int:id>', views.BankView.as_view(), name='viewbank'),
    path('add', views.BanksCreate.as_view(), name='bankadd'),
    path('updatebankstatus/<int:id>', views.BankUpdateStatusView.as_view(), name='updatebankstatus'),
]
