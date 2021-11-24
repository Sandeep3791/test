from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.SettingList.as_view(), name='settings'),
    path('settings_update/<str:id>/',
         views.update_settings, name='settings_update'),
]
