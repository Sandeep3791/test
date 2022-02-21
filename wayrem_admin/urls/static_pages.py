from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.StaticpagesList.as_view(), name='staticpages'),
    path('add', views.StaticpagesCreate.as_view(), name='addstaticpages'),
    path('<int:static_pages_pk>', views.StaticpagesUpdate.as_view(),
         name='updatestaticpages'),
    path('view/<int:static_pages_pk>',
         views.StaticpagesView.as_view(), name='viewstaticpages'),
    path('<str:url>',
         views.staticpages_view, name='static_template'),


]
