from wayrem_admin.models import PaymentTransaction
from email import message
import imp
from urllib import response
from django.views.decorators.csrf import csrf_exempt
from grpc import Status
from wayrem_admin.loginext.webhook_liberary import WebHookLiberary
from django.http import HttpResponse
import json
from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary
from wayrem_admin.services import send_email
from wayrem_admin.forms import CustomerSearchFilter, CustomerEmailUpdateForm
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
from wayrem_admin.models import Customer, EmailTemplateModel, CustomerDevice, Settings
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
        qs = Customer.objects.filter().order_by("-id")
        filtered_list = CustomerFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CustomersList, self).get_context_data(**kwargs)
        context['filter_form'] = CustomerSearchFilter(self.request.GET)
        return context


# class CustomersList(View):
#     template_name = "customerlist.html"

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
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
    return render(request, 'customer/customer_view.html', {'user': user})


def customer_verification(request, id=None):
    status = request.GET.get('status')
    print(status)
    user = Customer.objects.filter(id=id).first()
    customer_id = user.id
    email_id = user.email
    full_name = f"{user.first_name} {user.last_name}"
    if status:
        user.verification_status = status
        user.reject_reason = None
        user.save()
    else:
        user.verification_status = "rejected"
        reason = request.POST.get('reason')
        user.reject_reason = reason
        user.save()
        email_template = EmailTemplateModel.objects.get(
            key="customer_rejected")
        subject = email_template.subject
        values = {
            "customer": full_name,
            "reason": reason
        }
        body = email_template.message_format.format(**values)
        send_email(to=email_id, subject=subject, body=body)
        try:
            devices = CustomerDevice.objects.filter(
                customer=customer_id, is_active=True)
            setting_key = "notification_customer_rejected"
            setting_msg = Settings.objects.get(key=setting_key)
            message = setting_msg.value
            print(devices)
            if not devices:
                print("No device found!!")
            else:
                for device in devices:
                    device_token = device.device_id
                    notf = {
                        "title": "Rejected",
                        "message": message,
                        "device_token": device_token,
                        "order_id": None,
                        "grocery_id": None,
                        "profile_document": "profile_document"
                    }
                    FirebaseLibrary().push_notification_in_firebase(notf)
        except:
            pass
        # messages.success(request, f"{user.first_name} is now Rejected")
        return redirect('wayrem_admin:customerdetails', id)
    if status == "active":
        email_template = EmailTemplateModel.objects.get(
            key="customer_approved")
        subject = email_template.subject
        values = {
            "customer": full_name
        }
        body = email_template.message_format.format(**values)
        send_email(to=email_id, subject=subject, body=body)
        try:
            devices = CustomerDevice.objects.filter(
                customer=customer_id, is_active=True)
            setting_key = "notification_customer_approved"
            setting_msg = Settings.objects.get(key=setting_key)
            message = setting_msg.value
            print(devices)
            if not devices:
                print("No device found!!")
            else:
                for device in devices:
                    device_token = device.device_id
                    notf = {
                        "title": "Verified",
                        "message": message,
                        "device_token": device_token,
                        "order_id": None,
                        "grocery_id": None
                    }
                    FirebaseLibrary().push_notification_in_firebase(notf)
        except:
            pass
        messages.success(request, f"{user.first_name} is now Active")
    else:
        messages.error(request, f"{user.first_name} is now Inactive")
    return redirect('wayrem_admin:customerslist')


def customer_email_update(request, id=None):
    customer = Customer.objects.get(id=id)
    email_id = customer.email
    full_name = f"{customer.first_name} {customer.last_name}"
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        form = CustomerEmailUpdateForm(request.POST or None, instance=customer)
        if form.is_valid():
            form.save()
            new_email = form.data['email']
            email_template = EmailTemplateModel.objects.get(
                key="customer_email_update")
            subject = email_template.subject
            values = {
                # "customer": full_name,
                "customer_name": full_name,
                "updated_email": new_email
            }
            body = email_template.message_format.format(**values)
            send_email(to=email_id, subject=subject, body=body)
            return redirect('wayrem_admin:customerslist')
    else:
        form = CustomerEmailUpdateForm(instance=customer)
    return render(request, 'customer_email_update.html', {'form': form, 'id': customer.id})


class PaymentForm(View):
    template_name = "customer/payment_form.html"

    def get(self, request):
        checkout_id = request.GET.get("checkout_id")
        return render(self.request, self.template_name, {"checkoutId": checkout_id})


@method_decorator(csrf_exempt, name='dispatch')
class HyperpayPayment(View):
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        print(body)
        data = PaymentTransaction(response_body=str(body))
        print(data)
        data.save()
        return HttpResponse({"message": "Success"})


@method_decorator(csrf_exempt, name='dispatch')
class HyperpayRegistration(View):

    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        data = PaymentTransaction(response_body=body)
        print(data)
        data.save()
        return HttpResponse({'message': 'Success'})


@method_decorator(csrf_exempt, name='dispatch')
class HyperpayRisk(View):

    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        data = PaymentTransaction(response_body=body)
        data.save()
        return HttpResponse({'message': 'Success'})
