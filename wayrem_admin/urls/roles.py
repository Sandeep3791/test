from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.RoleList.as_view(), name='roles_list'),
    #path('list/', views.rolesList, name='roles_list'),
    path('create', views.RoleCreate.as_view(), name='roles_create'),
    #path('create/', views.createRoles, name='roles_create'),
    path('update/<int:role_pk>', views.RoleUpdate.as_view(), name='roles_update'),

    #path('update/', views.cupdateRoles, name='roles_update'),
    path('view/', views.RolePermissionViewReadOnly.as_view(), name='roles_view'),
    path('activeUnactive/', views.activeUnactiveRoles,
         name='roles_active_unactive'),
    path('permission/<int:id>/', views.RolePermissionView.as_view(),
         name='role-permission'),
]
