import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Customer
from wayrem_admin.decorators import role_required
from wayrem_admin.export import generate_pdf, generate_excel
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def customers_excel(request):
    return generate_excel("customers_master", "customers")


class CustomersList(View):
    template_name = "customerlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Customer Profile View'))
    def get(self, request, format=None):
        userlist = Customer.objects.all()
        paginator = Paginator(userlist, 25)
        page = request.GET.get('page')
        try:
            clist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            clist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            clist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"userlist": clist})


class Active_BlockCustomer(View):
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Customer Profile Edit'))
    def get(self, request, id):
        user = Customer.objects.filter(id=id).first()
        if user.status:
            user.status = False
        else:
            user.status = True
        user.save()
        return redirect('wayrem_admin:customerslist')


@role_required('Customer Profile View')
def customer_details(request, id=None):
    user = Customer.objects.filter(id=id).first()
    return render(request, 'customer_view.html', {'userdata': user})
