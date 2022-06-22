import re
from django.urls import reverse_lazy
from django.views.generic import ListView
from wayrem_admin.filters.category_filters import *
from wayrem_admin.utils.constants import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wayrem_admin.forms import CategoryCreateForm
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.forms.categories import CategoryForm, CategorySearchFilter, CategoryUpdateForm
from wayrem_admin.models import Categories
from wayrem_admin.export import generate_excel
from wayrem_admin.services import inst_Category
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import permission_required
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin


def categories_excel(request):
    return generate_excel("categories_master", "categories")


class CategoriesList(LoginPermissionCheckMixin, ListView):
    permission_required = 'categories.list'
    model = Categories
    template_name = "category/list.html"
    context_object_name = 'categorieslist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:categorieslist')

    def get_queryset(self):
        qs = Categories.objects.filter()
        filtered_list = CategoriesFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CategoriesList, self).get_context_data(**kwargs)
        context['filter_form'] = CategorySearchFilter(self.request.GET)
        return context


@login_required(login_url='wayrem_admin:root')
@permission_required('categories.edit', raise_exception=True)
def update_categories(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        category = Categories.objects.get(id=id)
        checkParent = Categories.objects.filter(parent=category.name)
        form = CategoryUpdateForm(
            request.POST or None, request.FILES or None, instance=category)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            parent = form.cleaned_data.get('parent_category')
            image = form.cleaned_data.get('image')
            margin = form.cleaned_data.get('margin')
            unit = form.cleaned_data.get('unit')
            tag = form.cleaned_data.get('tag')
            if checkParent:
                for cat in checkParent:
                    cat.parent = name
                    cat.save()
            category.name = name
            category.image = image
            category.margin = margin
            category.unit = unit
            category.tag = tag
            if parent:
                category.parent = parent
                category.is_parent = True
            else:
                category.parent = None
                category.is_parent = False
            category.save()
            return redirect('wayrem_admin:categorieslist')
    category = Categories.objects.get(id=id)
    form = CategoryUpdateForm(instance=category, initial={
                              'parent_category': category.parent
                              })
    return render(request, 'update_category.html', {'form': form, 'id': category.id, 'user': category})


@permission_required('categories.view', raise_exception=True)
def category_details(request, id=None):
    cate = Categories.objects.filter(id=id).first()
    return render(request, 'category_popup.html', {'catedata': cate})


class DeleteCategories(LoginPermissionCheckMixin, View):
    permission_required = 'categories.delete'

    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = Categories.objects.get(id=categoriesid)
        category_name = categories.name
        categories.delete()
        isParentCheck = Categories.objects.filter(parent=category_name)
        if isParentCheck:
            for category in isParentCheck:
                category.is_parent = False
                category.parent = None
                category.save()
        return redirect('wayrem_admin:categorieslist')


@permission_required('categories.add', raise_exception=True)
def add_category(request):
    context = {}
    form = CategoryForm(request.POST or None, request.FILES or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            if request.POST.get('parent_category'):
                subcategory = Categories()
                subcategory.name = form.cleaned_data.get('name')
                subcategory.image = form.cleaned_data.get('image')
                subcategory.tag = form.cleaned_data.get('tag')
                subcategory.margin = form.cleaned_data.get('margin')
                subcategory.unit = form.cleaned_data.get('unit')
                subcategory.parent = form.cleaned_data.get('parent_category')
                subcategory.is_parent = True
                subcategory.save()
                return redirect('wayrem_admin:categorieslist')

            else:
                category = Categories()
                category.name = form.cleaned_data.get('name')
                category.image = form.cleaned_data.get('image')
                category.tag = form.cleaned_data.get('tag')
                category.margin = form.cleaned_data.get('margin')
                category.unit = form.cleaned_data.get('unit')
                category.save()
                print('valid')
                return redirect('wayrem_admin:categorieslist')

        else:
            print("Invalid")
    return render(request, 'add_category.html', context)
