import re
from django.urls import reverse_lazy
from django.views.generic import ListView
from wayrem_admin.filters.category_filters import *
from wayrem_admin.utils.constants import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wayrem_admin.decorators import role_required
from wayrem_admin.forms import CategoryCreateForm
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.forms.categories import CategoryForm, CategorySearchFilter, CategoryUpdateForm
from wayrem_admin.models import Categories, SubCategories
from wayrem_admin.export import generate_excel
from wayrem_admin.services import inst_Category
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def categories_excel(request):
    return generate_excel("categories_master", "categories")


@login_required(login_url='wayrem_admin:root')
@role_required('Categories Add')
def create_category(request):
    context = {}
    form = CategoryCreateForm(request.POST or None, request.FILES or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            print('valid')
            form.save()
            return redirect('wayrem_admin:categorieslist')
        else:
            print("Invalid")
    return render(request, 'edit_categories.html', context)


class CategoriesList(ListView):
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


# class CategoriesList(View):
#     template_name = "categorieslist.html"

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     @method_decorator(role_required('Categories View'))
#     def get(self, request, format=None):
#         categorieslist = Categories.objects.all()
#         paginator = Paginator(categorieslist, 5)
#         page = request.GET.get('page')
#         try:
#             clist = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             clist = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             clist = paginator.page(paginator.num_pages)
#         return render(request, self.template_name, {"categorieslist": clist})


# class DeleteCategories(View):
#     def post(self, request):
#         categoriesid = request.POST.get('category_id')
#         categories = Categories.objects.get(id=categoriesid)
#         categories.delete()
#         return redirect('wayrem_admin:categorieslist')


@login_required(login_url='wayrem_admin:root')
@role_required('Categories Edit')
def update_categories(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        user = Categories.objects.get(id=id)
        form = CategoryUpdateForm(
            request.POST or None, request.FILES or None, instance=user)
        if form.is_valid():
            print("FORM")
            name = form.cleaned_data.get('name')
            parent = form.cleaned_data.get('parent_category')
            image = form.cleaned_data.get('image')
            margin = form.cleaned_data.get('margin')
            unit = form.cleaned_data.get('unit')
            tag = form.cleaned_data.get('tag')
            user.name = name
            user.image = image
            user.margin = margin
            user.unit = unit
            user.tag = tag
            if parent:
                user.parent = parent
                user.is_parent = True
            else:
                user.parent = None
                user.is_parent = False
            user.save()
            print("Here")
            return redirect('wayrem_admin:categorieslist')
    user = Categories.objects.get(id=id)
    form = CategoryUpdateForm(instance=user, initial={                              
                              'parent_category': user.parent                              
                              })
    return render(request, 'update_category.html', {'form': form, 'id': user.id, 'user':user})


@role_required('Categories View')
def category_details(request, id=None):
    cate = Categories.objects.filter(id=id).first()
    return render(request, 'category_popup.html', {'catedata': cate})


class DeleteCategories(View):
    @method_decorator(role_required('Categories Delete'))
    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = Categories.objects.get(id=categoriesid)
        categories.delete()
        return redirect('wayrem_admin:categorieslist')


@login_required(login_url='wayrem_admin:root')
@role_required('Categories Add')
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
