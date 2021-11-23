from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_po/', views.po_excel, name='excelpo'),
    path('purchase_order/', views.create_purchase_order, name='create_po'),
    path('po-list/', views.POList.as_view(), name='polist'),
    path('delete-po/', views.DeletePO.as_view(), name='deletepo'),
    path('view-po/<str:id>', views.viewpo, name='viewpo'),
    path('edit-po/<str:id>', views.editpo, name='editpo'),
    path('edit-po-status/<str:id>', views.statuspo, name='po_status'),

]
