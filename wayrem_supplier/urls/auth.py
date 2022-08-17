from django.urls import path
from wayrem_supplier import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('supplier-profile/', views.supplier_profile, name='supplier_profile'),
    path('update-supplier-profile/', views.update_supplier_profile,
         name='update_supplier_profile'),
    path('forgot-password/', views.forgot_password, name='forgot-pass'),
    path('reset-password/', views.reset_password, name='reset-pass'),
    path('notification-seen/<str:id>/',
         views.notifications_seen, name='notification-seen'),
    path('clear-notification/', views.notifications_clear,
         name='notification-clear'),
]
