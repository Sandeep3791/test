from django.shortcuts import render, redirect, get_object_or_404
from wayrem_admin.models import Roles
from wayrem_admin.decorators import role_required
from wayrem_admin.forms import RoleForm, RoleViewForm
from django.contrib import messages


@role_required('Roles View')
def rolesList(request):
    context = {}
    roles = Roles.objects.all().order_by('-pk')
    context['roles'] = roles
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
    return render(request, 'roles_crud_pages/createRoles.html', {"form": form})


@role_required('Roles Edit')
def cupdateRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    form = RoleForm(instance=role, label_suffix='')
    context['form'] = form
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(request, "Role Updated")
            return redirect('wayrem_admin:roles_list')
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
