from wayrem_admin.forms import CustomerSearchFilter
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.customer_filters import *
from django.views.generic import ListView
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


class CustomersList(ListView):
    model = Customer
    template_name = "customer/list.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:categorieslist')

    def get_queryset(self):
        qs = Customer.objects.filter()
        filtered_list = CustomerFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CustomersList, self).get_context_data(**kwargs)
        context['filter_form'] = CustomerSearchFilter(self.request.GET)
        return context


# class CustomersList(View):
#     template_name = "customerlist.html"

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     @method_decorator(role_required('Customer Profile View'))
#     def get(self, request, format=None):
#         userlist = Customer.objects.all()
#         paginator = Paginator(userlist, 5)
#         page = request.GET.get('page')
#         try:
#             clist = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             clist = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             clist = paginator.page(paginator.num_pages)
#         return render(request, self.template_name, {"userlist": clist})


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
    return render(request, 'customer/customer_view.html', {'user': user})


@role_required('Customer Profile View')
def customer_verification(request, id=None):
    status = request.GET.get('status')
    user = Customer.objects.filter(id=id).first()
    user.verification_status = status
    user.save()
    if status == "active":
        messages.success(request, f"{user.first_name} is now Active")
    else:
        messages.error(request, f"{user.first_name} is now Inactive")
    return redirect('wayrem_admin:customerslist')
