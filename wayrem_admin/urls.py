from django.urls import path
from wayrem_admin import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('forgot-pass/', views.forgot_pass, name='forgotpass'),
    path('reset-pass/', views.reset_password, name='resetpassword'),
    path('forgot-api/', views.OtpApi.as_view(), name='forgotpassapi'),
    path('resetpassword/', views.ResetPassword.as_view(), name='reset'),
    path('reset-api/', views.Reset_Password.as_view(), name='resetpassapi'),
    #     path('', views.admin_login, name='log'),
    path('', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('userlist/', views.UsersList.as_view(), name='userlist'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    #     path('adminlogin/', views.admin_login, name='adminlogin'),
    path('apicustom/register/', views.CustomRegisterAPI.as_view(),
         name='apicustomregister'),
    path('apirole/register/', views.RoleAPI.as_view(),
         name='roleapi'),
    # path('api/forget/', views.ForgetAPI.as_view(),
    #         name='forgetapi'),
]
