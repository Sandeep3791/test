from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wayrem_admin.forms import CategoryCreateForm
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Categories
from wayrem_admin.export import generate_pdf, generate_excel


def categories_excel(request):
    return generate_excel("categories_master", "categories")


def pdf_category(request):
    query = 'SELECT id, name, category_image, description, created_at, updated_at FROM categories_master'
    template = "pdf_category.html"
    file = "categories.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


@login_required(login_url='wayrem_admin:root')
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


class CategoriesList(View):
    template_name = "categorieslist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        categorieslist = Categories.objects.all()
        # user_role = Roles.objects.all()
        # "roles":user_role
        return render(request, self.template_name, {"categorieslist": categorieslist})


class DeleteCategories(View):
    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = Categories.objects.get(id=categoriesid)
        categories.delete()
        return redirect('wayrem_admin:categorieslist')


@login_required(login_url='wayrem_admin:root')
def update_categories(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        user = Categories.objects.get(id=id)
        form = CategoryCreateForm(
            request.POST or None, request.FILES or None, instance=user)
        if form.is_valid():
            print("FORM")
            name = form.cleaned_data['name']
            category_image = form.cleaned_data['category_image']
            description = form.cleaned_data['description']
            user.name = name
            user.category_image = category_image
            user.description = description
            user.save()
            print("Here")
            return redirect('wayrem_admin:categorieslist')
    user = Categories.objects.get(id=id)
    form = CategoryCreateForm(instance=user)
    return render(request, 'update_category.html', {'form': form, 'id': user.id})


def category_details(request, id=None):
    cate = Categories.objects.filter(id=id).first()
    return render(request, 'category_popup.html', {'catedata': cate})


class DeleteCategories(View):
    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = Categories.objects.get(id=categoriesid)
        categories.delete()
        return redirect('wayrem_admin:categorieslist')
