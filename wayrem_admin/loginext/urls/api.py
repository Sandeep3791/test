from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from wayrem_admin.loginext.views import api_views
 

urlpatterns = [
    path('',api_views.LogiNextAPI.as_view({'get':'test'}),name='test')
]
