from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_settings/', views.settings_excel, name='excelsettings'),
    path('list/', views.SettingList.as_view(), name='settingslist'),
    path('settings_update/<str:id>/',
         views.update_settings, name='settings_update'),
    path('create_setting/', views.CreateSetting.as_view(), name='settings'),
    
         

]
