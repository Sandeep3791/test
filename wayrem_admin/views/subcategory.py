from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wayrem_admin.forms import SubCategoryCreateForm
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import SubCategories
from wayrem_admin.export import generate_excel


def subcategories_excel(request):
    return generate_excel("subcategories_master", "subcategories")



@login_required(login_url='wayrem_admin:root')
def create_subcategory(request):
    context = {}
    form = SubCategoryCreateForm(request.POST or None, request.FILES or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            print('valid')
            form.save()
            return redirect('wayrem_admin:subcategorieslist')
        else:
            print("Invalid")
    return render(request, 'create_subcategory.html', context)


class SubCategoriesList(View):
    template_name = "subcategorieslist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        categorieslist = SubCategories.objects.all()
        return render(request, self.template_name, {"categorieslist": categorieslist})


class DeleteSubCategories(View):
    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = SubCategories.objects.get(id=categoriesid)
        categories.delete()
        return redirect('wayrem_admin:subcategorieslist')


@login_required(login_url='wayrem_admin:root')
def update_subcategories(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        user = SubCategories.objects.get(id=id)
        form = SubCategoryCreateForm(
            request.POST or None, request.FILES or None, instance=user)
        if form.is_valid():
            print("FORM")
            form.save()
            return redirect('wayrem_admin:subcategorieslist')
    user = SubCategories.objects.get(id=id)
    form = SubCategoryCreateForm(instance=user)
    return render(request, 'update_subcategory.html', {'form': form, 'id': user.id})


def subcategory_details(request, id=None):
    cate = SubCategories.objects.filter(id=id).first()
    return render(request, 'category_popup.html', {'catedata': cate})
