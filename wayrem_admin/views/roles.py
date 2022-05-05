from django.shortcuts import render, redirect, get_object_or_404
from wayrem_admin.models import Roles
from wayrem_admin.decorators import role_required
from wayrem_admin.forms import RoleForm, RoleViewForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.utils.constants import *

from django.views.generic import View
from wayrem_admin.permissions.models import FunctionMaster,RolePermissions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

class RolePermissionView(View):
    template_name = 'permissions/role_permission.html'
    def get(self, request, *args, **kwargs):
        role_id = self.kwargs['id']
        role = get_object_or_404(Roles, pk=role_id)
        exist_permission = RolePermissions.objects.filter(role_id=role.id).all()
        exist_permission = list(exist_permission.values_list('function_id', flat=True))
        if self.request.is_ajax():
            self.template_name = 'permissions/permission_checkbox.html'
        pages_menu = FunctionMaster.objects.filter(Q(status=1) & Q(show_in_permission="yes")).order_by('display_order')        
        
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
        ctx = {'function_list':pages_menu_dict, 'exist_permission':exist_permission,'id_param':role_id}       
        return render(request, self.template_name, ctx)
    
    def post(self, request, *args, **kwargs):
        role_id = self.kwargs['id']
        role = get_object_or_404(Roles, pk=role_id)
        exist_permission = RolePermissions.objects.select_related('function').filter(role_id=role.id).all()
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
        return HttpResponse("Menu Permission Set")

@role_required('Roles View')
def rolesList(request):
    context = {}
    roles = Roles.objects.all().order_by('-pk')
    paginator = Paginator(roles, RECORDS_PER_PAGE)
    page = request.GET.get('page')
    try:
        rolelist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rolelist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rolelist = paginator.page(paginator.num_pages)
    context['roles'] = rolelist
    return render(request, 'roles_crud_pages/rolesList.html', context)


@role_required('Roles Add')
def createRoles(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            print("not valid")
            form.save()
            messages.success(request, "Role Added")
            return redirect('wayrem_admin:roles_list')
    else:
        form = RoleForm(label_suffix='')
    # return render(request, 'roles_crud_pages/create_role.html', {"form": form})
    return render(request, 'roles_crud_pages/createRoles.html', {"form": form})


@role_required('Roles Edit')
def cupdateRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(request, "Role Updated")
            return redirect('wayrem_admin:roles_list')
        else:
            context['form'] = form
    else:
        form = RoleForm(instance=role, label_suffix='')
        context['form'] = form
    return render(request, 'roles_crud_pages/createRoles.html', context)


@role_required('Roles Delete')
def activeUnactiveRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    if role.status == "Active":
        role.status = 'Inactive'
    else:
        role.status = 'Active'
    role.save()
    messages.success(request, "Role Updated")
    return redirect('wayrem_admin:roles_list')


def viewRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    form = RoleViewForm(instance=role, label_suffix='')
    context['form'] = form
    context['role_name'] = Roles.objects.get(id=request.GET.get('id'))
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(request, "Role Updated")
            return redirect('wayrem_admin:roles_list')
    return render(request, 'roles_crud_pages/view_roles.html', context)
