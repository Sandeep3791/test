import threading
from django.db.models import Q
from django.db.models import Sum
from django.views.generic.edit import CreateView
from matplotlib.style import available
from requests import request
from wayrem_admin.forms.customers import CreditsAssignForm
from wayrem_admin.models import PaymentTransaction, CreditManagement, CreditPaymentReference
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
from wayrem_admin.models.customers import CustomerNotification
from wayrem_admin.models.orders import Orders, StatusMaster
from wayrem_admin.services import send_email
from wayrem_admin.forms import CustomerSearchFilter, CustomerEmailUpdateForm, CreditsForm, CreditsSearchFilter
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.customer_filters import *
from django.views.generic import ListView, UpdateView
import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Customer, EmailTemplateModel, CustomerDevice, Settings, CreditTransactionLogs
from wayrem_admin.export import generate_pdf, generate_excel
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta


class CreditCreate(LoginPermissionCheckMixin, CreateView):
    permission_required = 'credits.settings_add'
    model = CreditSettings
    form_class = CreditsForm
    template_name = 'credits/add.html'
    success_url = reverse_lazy('wayrem_admin:credits_list')

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(CreditCreate, self).dispatch(*args, **kwargs)


class CreditsList(LoginPermissionCheckMixin, ListView):
    permission_required = 'credits.settings'
    model = CreditSettings
    template_name = "credits/list.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:credits_list')

    def get_queryset(self):
        qs = CreditSettings.objects.filter().order_by("-id")
        filtered_list = CreditsFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CreditsList, self).get_context_data(**kwargs)
        context['filter_form'] = CreditsSearchFilter(self.request.GET)
        return context


class CreditUpdate(LoginPermissionCheckMixin, UpdateView):
    permission_required = 'credits.settings_edit'
    model = CreditSettings
    form_class = CreditsForm
    template_name = 'credits/update.html'
    pk_url_kwarg = 'credit_pk'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(CreditUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:update_credit', kwargs={'credit_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credit_pk = self.kwargs['credit_pk']
        context['credit_pk'] = credit_pk
        return context


class CreditView(LoginPermissionCheckMixin, UpdateView):
    permission_required = 'credits.settings_view'
    model = CreditSettings
    form_class = CreditsForm
    template_name = 'credits/view.html'
    pk_url_kwarg = 'credit_pk'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(CreditView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:view_credit', kwargs={'credit_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credit_pk = self.kwargs['credit_pk']
        context['credit_pk'] = credit_pk
        return context


class CreditAssign(LoginPermissionCheckMixin, View):
    permission_required = 'credits.assign_customer'
    form = CreditsAssignForm()

    def get(self, request, id):
        try:
            existing_credit_check = CreditManagement.objects.get(
                customer_id=id)
            existing_credit = existing_credit_check.credit_rule
        except:
            existing_credit = None
        self.form = CreditsAssignForm(initial={'credit': existing_credit})
        return render(request, "customer/credit_assign.html", {"form": self.form})

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def post(self, request, id):
        form = CreditsAssignForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data("credit")
            credit_setting = CreditSettings.objects.get(id=credit)
            assign_credit = CreditManagement(
                customer=id, credit_rule=credit, used=0, available=credit_setting.credit_amount)
            assign_credit.save()
        return redirect('wayrem_admin:customerslist')


@permission_required('credits.assign_customer', raise_exception=True)
def creditAssign(request, id=None):
    data = request.POST.copy()
    data['id'] = id
    try:
        existing_credit_check = CreditManagement.objects.get(
            customer_id=id)
        existing_credit = existing_credit_check
    except:
        existing_credit = None
    if request.method == "POST":
        form = CreditsAssignForm(data)
        if form.is_valid():
            credit = form.cleaned_data.get("credit")
            available_credit = CreditSettings.objects.get(id=credit)
            if existing_credit:
                existing_credit.credit_rule_id = available_credit
                existing_credit.available = available_credit.credit_amount - existing_credit.used
                existing_credit.save()
            else:
                assign_credit = CreditManagement(
                    customer_id=id, credit_rule=available_credit, used=0, available=available_credit.credit_amount)
                assign_credit.save()
            messages.success(request, "Credit Updated!")
            return redirect('wayrem_admin:customerslist')
        else:
            return render(request, "customer/credit_assign.html", {"form": form, "id": id})
    if existing_credit:
        form = CreditsAssignForm(
            initial={'credit': existing_credit.credit_rule.id})
    else:
        form = CreditsAssignForm(initial={'credit': existing_credit})
    return render(request, "customer/credit_assign.html", {"form": form, "id": id})


class CustomerCreditTransactionLogs(LoginPermissionCheckMixin, ListView):
    permission_required = 'credits.transaction_logs'
    model = CreditTransactionLogs
    template_name = "credits/transaction_logs.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:customerslist')
    total_credit = 0
    total_debit = 0

    def get_queryset(self):
        qs = CreditTransactionLogs.objects.filter(
            customer=self.kwargs['customer_id']).order_by("-id")
        qs = qs.filter(Q(Q(reference=None) |
                       Q(reference__payment_status_id=7)))
        self.total_credit = qs.aggregate(
            total=Sum('credit_amount'))['total'] or 0
        self.total_debit = qs.aggregate(total=Sum('paid_amount'))['total'] or 0
        return qs

    def get_context_data(self, **kwargs):
        context = super(CustomerCreditTransactionLogs,
                        self).get_context_data(**kwargs)
        context['customer'] = get_object_or_404(
            Customer, id=self.kwargs['customer_id'])
        context['total_credit'] = round(self.total_credit, 2)
        context['total_debit'] = round(self.total_debit, 2)
        return context


def credit_reminder():
    credit_management = CreditManagement.objects.all()
    for credit in credit_management:
        credit_logs = CreditTransactionLogs.objects.filter(
            customer=credit.customer)
        print(credit.customer)
        if credit_logs:
            for log in credit_logs:
                credit_paid = CreditTransactionLogs.objects.filter(
                    credit_id=log.id, payment_status=True).first()
                if not credit_paid:
                    today = datetime.today()
                    days_reminder1 = round(
                        abs(credit.credit_rule.time_period/2))
                    days_reminder2 = abs(
                        credit.credit_rule.time_period - 3)
                    reminder1 = log.credit_date + \
                        timedelta(days=days_reminder1)
                    reminder2 = log.credit_date + \
                        timedelta(days=days_reminder2)
                    if today.date() == reminder1.date() or today.date() == reminder2.date():
                        devices = CustomerDevice.objects.filter(
                            customer=credit.customer, is_active=True)
                        setting_msg = Settings.objects.get(
                            key="credit_reminder")
                        email_template = EmailTemplateModel.objects.get(
                            key="credit_reminder")
                        body_format = {
                            'customer': f"{log.customer.first_name} {log.customer.last_name}",
                            'amount': log.credit_amount,
                            'date': log.due_date
                        }
                        email_body = email_template.message_format.format(
                            **body_format)
                        t = threading.Thread(target=send_email, args=(
                            log.customer.email, email_template.subject, email_body))
                        t.start()
                        notify_title = setting_msg.display_name
                        values = {
                            'amount': log.credit_amount,
                            'date': log.due_date
                        }
                        message = setting_msg.value.format(**values)
                        print(devices)
                        if not devices:
                            return "No device found!!"
                        else:
                            for device in devices:
                                device_token = device.device_id
                                notf = {
                                    "title": notify_title,
                                    "message": message,
                                    "device_token": device_token,
                                }
                                payload = {
                                    "action_type": "credit_settlement",
                                    "amount": log.credit_amount,
                                    "id": log.id
                                }
                                FirebaseLibrary().send_firebase_notification(notf, payload)
                            notification_store = CustomerNotification(
                                customer=log.customer.id, title=notify_title, message=message)
                            notification_store.save()
    print("Credit Reminder Notification Done")


def credit_refund(order_id):
    order = Orders.objects.get(id=order_id)
    credit_log = CreditTransactionLogs.objects.filter(
        order=order, is_refund=False).first()
    credit_management = CreditManagement.objects.get(
        customer_id=credit_log.customer.id)
    credit_management.available += credit_log.credit_amount
    credit_management.used -= credit_log.credit_amount
    credit_management.save()
    refund_log = CreditTransactionLogs(customer=credit_management.customer, order=order,
                                       is_refund=True, available=credit_management.available, credit_id=credit_log.id, payment_status=True, paid_amount=credit_log.credit_amount)
    refund_log.save()
    return True


class CustomerCreditTransactionReference(LoginPermissionCheckMixin, ListView):
    permission_required = 'credits.paid_transaction_logs'
    model = CreditPaymentReference
    template_name = "credits/transaction_reference.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:customerslist')

    def get_queryset(self):
        qs = CreditPaymentReference.objects.all().order_by("-id")
        q = self.request.GET.get(
            'reference_no') if self.request.GET.get('reference_no') != None else ''
        if q != None:
            qs = qs.filter(reference_no__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super(CustomerCreditTransactionReference,
                        self).get_context_data(**kwargs)
        return context


class PaidCreditTransactionView(LoginPermissionCheckMixin, ListView):
    permission_required = 'credits.credit_transaction_approve'
    model = CreditTransactionLogs
    template_name = "credits/paid_transaction_view.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:customerslist')
    total_amount = 0

    def get_queryset(self):
        qs = CreditTransactionLogs.objects.filter(
            reference__reference_no=self.kwargs['reference_no']).order_by("-id")
        self.total_amount = qs.aggregate(
            total=Sum('paid_amount'))['total'] or 0
        return qs

    def get_context_data(self, **kwargs):
        context = super(PaidCreditTransactionView,
                        self).get_context_data(**kwargs)
        print(self.kwargs)
        try:
            context['payment_ref'] = get_object_or_404(
                CreditPaymentReference, reference_no=self.kwargs['reference_no'])
            context['customer'] = get_object_or_404(
                Customer, id=context['payment_ref'].customer.id)
            context['total_amount'] = round(self.total_amount, 2)
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        payment_status = request.POST.get("payment_status")
        payment_ref_id = request.POST.get("payment_ref_id")
        status = get_object_or_404(StatusMaster, id=payment_status)
        payment_ref = get_object_or_404(
            CreditPaymentReference, id=payment_ref_id)
        if status.id == 7:
            transactions = CreditTransactionLogs.objects.filter(
                reference=payment_ref)
            for trx in transactions:
                trx.payment_status = True
                trx.available += trx.paid_amount
                trx.available = round(trx.available, 2)
                trx.save()
            payment_ref.is_verified = True
        payment_ref.payment_status = status
        payment_ref.save()
        return HttpResponse("Successfully Updated")
