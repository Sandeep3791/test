from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.Forgot_Password.as_view(), name='forgot-password'),
    path('reset-password/', views.Reset_Password.as_view(), name='reset-password'),
    path('change-password/', views.Change_PasswordView.as_view(),
         name='change-password'),
]
