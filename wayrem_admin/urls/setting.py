from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_settings/', views.settings_excel, name='excelsettings'),
    path('list/', views.SettingList.as_view(), name='settingslist'),
    path('settings_update/<str:id>/',
         views.update_settings, name='settings_update'),
    path('create_setting/', views.CreateSetting.as_view(), name='settings'),
    
    path('localization-list',views.MobileLocalizationList.as_view(),name='localization_list'),
    path('excel_export',views.MobileLocalizationExport.as_view(),name='excel_export'),
    path('localization_excel_import',views.MobileLocalizationImport.as_view(),name='localization_excel_import'),


]
