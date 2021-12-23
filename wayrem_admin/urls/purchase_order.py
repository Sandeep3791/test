from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_po/', views.po_excel, name='excelpo'),
    path('pdf_po/', views.po_pdf, name='pdf_po'),
    path('confirm_delivery/', views.confirm_delivery, name='confirm_delivery'),
    path('purchase_order/', views.create_purchase_order, name='create_po'),
    path('purchase_order2/', views.create_po_step2, name='create_po2'),
    path('delete_inserted/<str:id>',
         views.delete_inserted_item, name='delete_inserted'),
    path('po-list/', views.POList.as_view(), name='polist'),
    path('delete-po/', views.DeletePO.as_view(), name='deletepo'),
    path('view-po/<str:id>', views.viewpo, name='viewpo'),
    path('edit-po/<str:id>', views.editpo, name='editpo'),
    path('delete-in-edit/<str:id>', views.delete_in_edit, name='delete_in_edit'),
    path('edit-po-status/<str:id>', views.statuspo, name='po_status'),

]
