import re
from django.views.generic.edit import CreateView
from requests import request
from wayrem_admin.forms.customers import CreditsAssignForm
from wayrem_admin.models import PaymentTransaction, CreditManagement
from email import message
import imp
from urllib import response
from django.views.decorators.csrf import csrf_exempt
from grpc import Status
from wayrem_admin.loginext.webhook_liberary import WebHookLiberary
from django.http import HttpResponse
import json
from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary
from wayrem_admin.models import CreditSettings
from wayrem_admin.models.orders import Orders
from wayrem_admin.services import send_email
from wayrem_admin.forms import CustomerSearchFilter, CustomerEmailUpdateForm, CreditsForm, CreditsSearchFilter
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.customer_filters import *
from django.views.generic import ListView, UpdateView
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
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
import threading
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def customers_excel(request):
    return generate_excel("customers_master", "customers")


class CustomersList(LoginPermissionCheckMixin, ListView):
    permission_required = 'customer.list'
    model = Customer
    template_name = "customer/list.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:customerslist')

    def get_queryset(self):
        qs = Customer.objects.filter(status=True).order_by("-id")
        filtered_list = CustomerFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CustomersList, self).get_context_data(**kwargs)
        context['filter_form'] = CustomerSearchFilter(self.request.GET)
        return context


class Active_BlockCustomer(LoginPermissionCheckMixin, View):
    permission_required = 'customer.approve'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, id):
        user = Customer.objects.filter(id=id).first()
        if user.status:
            user.status = False
        else:
            user.status = True
        user.save()
        return redirect('wayrem_admin:customerslist')


@permission_required('customer.view', raise_exception=True)
def customer_details(request, id=None):
    user = Customer.objects.filter(id=id).first()
    return render(request, 'customer/customer_view.html', {'user': user})


@permission_required('customer.approve', raise_exception=True)
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

        # send_email(to=email_id, subject=subject, body=body)
        t = threading.Thread(
            target=send_email, args=(email_id, subject, body))
        t.start()
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
        except Exception as e:
            print("Failed to send notifications because ", e)
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
        # send_email(to=email_id, subject=subject, body=body)
        t = threading.Thread(
            target=send_email, args=(email_id, subject, body))
        t.start()
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
        except Exception as e:
            print("Failed to send emails because", e)
        messages.success(request, f"{user.first_name} is now Active")
    else:
        messages.error(request, f"{user.first_name} is now Inactive")
    return redirect('wayrem_admin:customerslist')


@permission_required('customer.update_email', raise_exception=True)
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
            # send_email(to=email_id, subject=subject, body=body)
            t = threading.Thread(
                target=send_email, args=(email_id, subject, body))
            t.start()
            return redirect('wayrem_admin:customerslist')
    else:
        form = CustomerEmailUpdateForm(instance=customer)
    return render(request, 'customer/customer_email_update.html', {'form': form, 'id': customer.id})


class PaymentForm(View):
    template_name = "customer/payment_form.html"

    def get(self, request):
        checkout_id = request.GET.get("checkout_id")
        return render(self.request, self.template_name, {"checkoutId": checkout_id})


@method_decorator(csrf_exempt, name='dispatch')
class HyperpayPayment(View):
    SUCCESS_CODES_REGEX = re.compile(r'^(000\.000\.|000\.100\.1|000\.[36])')
    key_from_configuration = "CC280328FF984554CF1605BC0B5545840A45486DE4101D5C60017D287D493E16"

    @csrf_exempt
    def post(self, request, **kwargs):
        data = {}
        iv_from_http_header = request.headers.get("X-Initialization-Vector")
        auth_tag_from_http_header = request.headers.get("X-Authentication-Tag")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        http_body = body.get("encryptedBody")
        key = binascii.unhexlify(self.key_from_configuration)
        iv = binascii.unhexlify(iv_from_http_header)
        auth_tag = binascii.unhexlify(auth_tag_from_http_header)
        cipher_text = binascii.unhexlify(http_body)
        # Prepare decryption
        decryptor = Cipher(algorithms.AES(key), modes.GCM(
            iv, auth_tag), backend=default_backend()).decryptor()

        # Decrypt
        result_bytes = decryptor.update(cipher_text) + decryptor.finalize()
        result_decode = result_bytes.decode('utf-8')
        result = json.loads(result_decode)
        data['response_body'] = str(result)
        code = result.get("payload").get("result").get("code")
        data['transaction_id'] = result.get("payload").get("id")
        data['checkout_id'] = result.get("payload").get("ndc")
        data['payment_type'] = result.get("paymentType")
        data['payment_brand'] = result.get("paymentBrand")
        data['amount'] = result.get("amount")
        data['status'] = result.get("payload").get("result").get("description")
        try:
            order = Orders.objects.get(checkout_id=data['checkout_id'])
            # data['order_id'] = order.id
        except:
            pass
        if re.search(self.SUCCESS_CODES_REGEX, code):
            pass
        payment_transaction = PaymentTransaction(**data)
        payment_transaction.save()
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
