from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_settings/', views.settings_excel, name='excelsettings'),
    path('pdf_settings/', views.pdf_settings, name='settingspdf'),
    path('list/', views.SettingList.as_view(), name='settings'),
    path('settings_update/<str:id>/',
         views.update_settings, name='settings_update'),

]
