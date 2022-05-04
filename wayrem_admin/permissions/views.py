from django.shortcuts import render
from permissions.mixins import LoginPermissionCheckMixin
from django.views.generic import View
from django.http import HttpResponseRedirect
from permissions.models import FunctionMaster, UserPermissions, RolePermissions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from users.models import Users
from roles.models import Roles
from django.contrib import messages
import sys, os
from django.conf import settings

class UserPermissionView(LoginPermissionCheckMixin, View):
    permission_required = 'users.permission_user'      
    template_name = 'permissions/user_permission.html'
    pk_url_kwarg = 'id'
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['id']
        module_id = self.kwargs['module_id']                 
        user = get_object_or_404(Users, pk=user_id)
        exist_permission = UserPermissions.objects.filter(Q(user_id=user.id)).all()
        if not exist_permission:
            exist_permission = RolePermissions.objects.filter(Q(role_id=user.role_id)).all()
        exist_permission = list(exist_permission.values_list('function_id', flat=True))
        if self.request.is_ajax():
            self.template_name = 'permissions/permission_checkbox.html'
        pages_menu = FunctionMaster.objects.filter(Q(status=1) & Q(module_id=module_id) & Q(show_in_permission="yes")).order_by('display_order')        
        pages_menu_list = []
        pages_menu_dict = {}
        menu_temp_dict = {}        
        sub_list = []
        if pages_menu:
            for menu in pages_menu:                
                if menu.parent_id == 0:
                    pages_menu_list.append(menu.id)                
                    menu_temp_dict[menu.id] = menu.__dict__
                                                     
            for function_id in pages_menu_list: 
                menu_dict = {}           
                menu_dict['menu'] = menu_temp_dict[function_id] 
                for menu in pages_menu:
                    if menu.parent_id == function_id:
                        sub_list.append(menu.__dict__)               
                if sub_list: 
                    menu_dict['submenu']  = sub_list.copy()                
                pages_menu_dict[function_id] = menu_dict
                sub_list.clear()
        ctx = {'function_list':pages_menu_dict, 'exist_permission':exist_permission,'id_param':user_id,'module_id':module_id}       
        return render(request, self.template_name, ctx)
     
    def post(self, request, *args, **kwargs):
        user_id = self.kwargs['id']
        module_id = request.POST['module_id']         
        user = get_object_or_404(Users, pk=user_id)
        exist_permission = UserPermissions.objects.select_related('function').filter(user_id=user.id,function__module_id= module_id).all()
        exist_permission = list(exist_permission.values_list('function_id', flat=True))
        new_permission = list(map(int, request.POST.getlist('permission')))        
        list_to_add = list(set(new_permission) - set(exist_permission))
        list_to_remove = list(set(exist_permission) - set(new_permission))        
        bulk_list_to_add = []
        print("list_to_add=",list_to_add)
        print("list_to_remove=",list_to_remove)
        if list_to_add:
            for function_id in list_to_add:
                bulk_list_to_add.append(UserPermissions(user_id=user_id, function_id=function_id))
        UserPermissions.objects.bulk_create(bulk_list_to_add)
        """remove permission if not selected from permission list"""
        if list_to_remove:
            UserPermissions.objects.filter(Q(user_id=user_id) & Q(function__in=list_to_remove)).delete()
        #print(request.POST.getlist('permission'))
        messages.success(self.request, 'Permission updated successfully.') 
        return HttpResponseRedirect("/permission/user/"+str(user_id)+"/"+str(module_id))
    
class RolePermissionView(LoginPermissionCheckMixin, View):
    permission_required = 'roles.permission_role'       
    template_name = 'permissions/role_permission.html'
    def get(self, request, *args, **kwargs):
        role_id = self.kwargs['id']
        module_id = self.kwargs['module_id']        
        role = get_object_or_404(Roles, pk=role_id)
        exist_permission = RolePermissions.objects.filter(role_id=role.id).all()
        exist_permission = list(exist_permission.values_list('function_id', flat=True))
        if self.request.is_ajax():
            self.template_name = 'permissions/permission_checkbox.html'
        pages_menu = FunctionMaster.objects.filter(Q(status=1) & Q(module_id=module_id) & Q(show_in_permission="yes")).order_by('display_order')        
        pages_menu_list = []
        pages_menu_dict = {}
        menu_temp_dict = {}        
        sub_list = []
        if pages_menu:
            for menu in pages_menu:                
                if menu.parent_id == 0:
                    pages_menu_list.append(menu.id)                
                    menu_temp_dict[menu.id] = menu.__dict__
                                                     
            for function_id in pages_menu_list: 
                menu_dict = {}           
                menu_dict['menu'] = menu_temp_dict[function_id] 
                for menu in pages_menu:
                    if menu.parent_id == function_id:
                        sub_list.append(menu.__dict__)               
                if sub_list: 
                    menu_dict['submenu']  = sub_list.copy()                
                pages_menu_dict[function_id] = menu_dict
                sub_list.clear()
        ctx = {'function_list':pages_menu_dict, 'exist_permission':exist_permission,'id_param':role_id,'module_id':module_id}       
        return render(request, self.template_name, ctx)
     
    def post(self, request, *args, **kwargs):
        role_id = self.kwargs['id']
        module_id = request.POST['module_id']        
        role = get_object_or_404(Roles, pk=role_id)
        exist_permission = RolePermissions.objects.select_related('function').filter(role_id=role.id,function__module_id= module_id).all()
        exist_permission = list(exist_permission.values_list('function_id', flat=True))
        new_permission = list(map(int, request.POST.getlist('permission')))        
        list_to_add = list(set(new_permission) - set(exist_permission))
        list_to_remove = list(set(exist_permission) - set(new_permission))        
        bulk_list_to_add = []
        if list_to_add:
            for function_id in list_to_add:
                bulk_list_to_add.append(RolePermissions(role_id=role_id, function_id=function_id))
        RolePermissions.objects.bulk_create(bulk_list_to_add)
        """remove permission if not selected from permission list"""
        if list_to_remove:
            RolePermissions.objects.filter(Q(role_id=role_id) & Q(function__in=list_to_remove)).delete()
        #print(request.POST.getlist('permission'))
        messages.success(self.request, 'Permission updated successfully.') 
        return HttpResponseRedirect("/permission/role/"+str(role_id)+"/"+str(module_id))      
        
        
def error_500(request):
        type, message, tb = sys.exc_info()        
        data = {'message':message}        
        return render(request,'500.html', data)
    
def error_404(request, *args, **kwargs):        
        return render(request,'404.html')
     
def error_403(request, *args, **kwargs):        
        return render(request,'403.html')   
