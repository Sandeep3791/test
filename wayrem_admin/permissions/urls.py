from django.urls import path
from permissions import views

urlpatterns = [
    path('user/<int:id>/<int:module_id>', views.UserPermissionView.as_view(), name='user-permission'),
    path('role/<int:id>/<int:module_id>', views.RolePermissionView.as_view(), name='role-permission'),
]
