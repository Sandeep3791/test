from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.rolesList, name='roles_list'),
    path('create/', views.createRoles, name='roles_create'),
    path('update/', views.cupdateRoles, name='roles_update'),
    path('view/', views.viewRoles, name='roles_view'),
    path('activeUnactive/', views.activeUnactiveRoles,name='roles_active_unactive'),
    path('role/<int:id>/<int:module_id>', views.RolePermissionView.as_view(), name='role-permission'),
]
