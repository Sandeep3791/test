from django.shortcuts import render, redirect, get_object_or_404
from wayrem_admin.models import Roles
from wayrem_admin.decorators import role_required
from wayrem_admin.forms import RoleForm, RoleViewForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@role_required('Roles View')
def rolesList(request):
    context = {}
    roles = Roles.objects.all().order_by('-pk')
    paginator = Paginator(roles, 5)
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
