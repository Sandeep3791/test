from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('pdf_user/', views.user_pdf, name='userpdf'),
    path('excel_user/', views.user_excel, name='exceluser'),
    path('users-registration/', views.user_signup, name='sub-admin-register'),
    path('users-list/', views.UsersList.as_view(), name='userlist'),
    path('user-details/<str:id>/', views.user_details, name='userdetails'),
    path('update-user/<str:id>/', views.update_user, name='updateuser'),
    path('update_profile/', views.update_profile, name='updateprofile'),
    path('deleteuser/', views.DeleteUser.as_view(), name='deleteuser'),
    path('activeblock/<str:id>/',
         views.Active_BlockUser.as_view(), name='activeblock'),
    path('excel_supplier/', views.supplier_excel, name='excelsupplier'),
    path('pdf_supplier/', views.supplier_pdf, name='supplierpdf'),
    path('supplier-registration/', views.supplier_register, name='suppregister'),
    path('supplier-list/', views.SupplierList.as_view(), name='supplierlist'),
    path('delete-supplier/', views.DeleteSupplier.as_view(), name='deletesupplier'),
    path('activeblock-supplier/<str:id>/',
         views.Active_BlockSupplier.as_view(), name='activeblocksupplier'),
    path('update-supplier/<str:id>/',
         views.update_supplier, name='updatesupplier'),
    path('supplier-details/<str:id>/',
         views.supplier_details, name='supplierdetails'),
]
