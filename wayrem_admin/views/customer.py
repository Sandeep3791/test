import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Customer
from wayrem_admin.export import generate_pdf, generate_excel


def categories_excel(request):
    return generate_excel("categories", "categories")


def pdf_category(request):
    query = 'SELECT id, name, category_image, description, created_at, updated_at FROM categories'
    template = "pdf_category.html"
    file = "categories.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


class CustomersList(View):
    template_name = "customerlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        userlist = Customer.objects.all()
        return render(request, self.template_name, {"userlist": userlist})


class Active_BlockCustomer(View):
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, id):
        user = Customer.objects.filter(id=id).first()
        if user.status:
            user.status = False
        else:
            user.status = True
        user.save()
        return redirect('wayrem_admin:customerslist')


def customer_details(request, id=None):
    user = Customer.objects.filter(id=id).first()
    return render(request, 'customer_view.html', {'userdata': user})
