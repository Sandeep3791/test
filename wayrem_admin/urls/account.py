from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_user/', views.user_excel, name='exceluser'),
    path('users-registration/', views.user_signup, name='sub-admin-register'),
    path('users-list/', views.UsersList.as_view(), name='userlist'),
    path('user-details/<str:id>/', views.user_details, name='userdetails'),
    path('update-user/<str:id>/', views.update_user, name='updateuser'),
    path('update_profile/', views.update_profile, name='updateprofile'),
    path('deleteuser/', views.DeleteUser.as_view(), name='deleteuser'),
    path('activeblock/<str:id>/',
         views.Active_BlockUser.as_view(), name='activeblock'),

]
