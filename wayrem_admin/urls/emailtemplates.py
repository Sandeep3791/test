from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.EmailtemplatesList.as_view(), name='emailtemplates'),
    path('add', views.EmailtemplatesCreate.as_view(), name='addemailtemplates'),
    path('<int:emailtemplate_pk>',views.EmailtemplatesUpdate.as_view(),name='updateemailtemplates'),
    path('view/<int:emailtemplate_pk>',views.EmailtemplatesView.as_view(),name='viewemailtemplates'),
   

]
