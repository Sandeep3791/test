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
from wayrem_admin.models.customers import CreditCycle, CustomerNotification
from wayrem_admin.models.orders import Orders, StatusMaster
from wayrem_admin.services import send_email
from wayrem_admin.forms import CustomerSearchFilter, CustomerEmailUpdateForm, CreditsForm, CreditsSearchFilter, CreditTxnSearchFilter
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
from datetime import datetime, timedelta, date, time


class CreditCreate(LoginPermissionCheckMixin, CreateView):
    permission_required = 'credits.settings_add'
    model = CreditSettings
    form_class = CreditsForm
    template_name = 'credits/add.html'
    success_url = reverse_lazy('wayrem_admin:credits_list')

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(CreditCreate, self).dispatch(*args, **kwargs)


class DeleteCredit(LoginPermissionCheckMixin, View):
    permission_required = 'credits.settings_delete'

    def post(self, request):
        creditId = request.POST.get('creditId')
        credit = CreditSettings.objects.get(id=creditId)
        check_credit = CreditManagement.objects.filter(credit_rule=credit)
        if check_credit:
            messages.error(request, "Credit Rule already assigned!")
        else:
            credit.delete()
            messages.success(request, "Credit Rule deleted!")
        return redirect('wayrem_admin:credits_list')


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
            credit_cycle, created = CreditCycle.objects.get_or_create(
                customer_id=id)
            date_today = date.today()
            min_startdate = datetime.combine(date_today, time.min)
            max_enddate = datetime.combine(
                date_today, time.max) + timedelta(days=available_credit.time_period)
            credit_cycle.start_date = min_startdate
            credit_cycle.end_date = max_enddate
            credit_cycle.credit_rule = available_credit
            credit_cycle.save()
            try:
                customer = Customer.objects.get(id=id)
                devices = CustomerDevice.objects.filter(
                    customer=customer, is_active=True)
                setting_msg = Settings.objects.get(
                    key="notification_credit_assign")
                email_template = EmailTemplateModel.objects.get(
                    key="notification_credit_assign")
                body_format = {
                    'customer': f"{customer.first_name} {customer.last_name}",
                    'amount': available_credit.credit_amount,
                    'days': available_credit.time_period
                }
                email_body = email_template.message_format.format(
                    **body_format)
                t = threading.Thread(target=send_email, args=(
                    customer.email, email_template.subject, email_body))
                t.start()
                notify_title = setting_msg.display_name
                values = {
                    'amount': available_credit.credit_amount,
                    'days': available_credit.time_period
                }
                message = setting_msg.value.format(**values)
                print(devices)
                if not devices:
                    print("No device found!!")
                else:
                    for device in devices:
                        device_token = device.device_id
                        notf = {
                            "title": notify_title,
                            "message": message,
                            "device_token": device_token,
                        }
                        payload = {
                            "action_type": "credit_assigned",
                            "amount": available_credit.credit_amount,
                            "credit": True
                        }
                        # FirebaseLibrary().send_firebase_notification(notf, payload)
                        t = threading.Thread(target=FirebaseLibrary().send_firebase_notification, args=(
                            notf, payload))
                        t.start()
                    notification_store = CustomerNotification(
                        customer=customer, title=notify_title, message=message)
                    notification_store.save()
            except Exception as e:
                print(e)
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
            customer=credit.customer, credit_id=None)
        print(credit.customer)
        if credit_logs:
            for log in credit_logs:
                credit_paid = CreditTransactionLogs.objects.filter(
                    credit_id=log.id, payment_status=True).first()
                if credit_paid:
                    pass
                else:
                    today = datetime.today()
                    days_reminder1 = round(
                        abs(credit.credit_rule.time_period/2))
                    days_reminder2 = abs(
                        credit.credit_rule.time_period - 3)
                    print(log.credit_date)
                    reminder1 = log.due_date - \
                        timedelta(days=days_reminder1)
                    reminder2 = log.due_date - \
                        timedelta(days=3)
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
                            'date': log.due_date.strftime("%A,%d %B, %Y")
                        }
                        email_body = email_template.message_format.format(
                            **body_format)
                        t = threading.Thread(target=send_email, args=(
                            log.customer.email, email_template.subject, email_body))
                        t.start()
                        notify_title = setting_msg.display_name
                        values = {
                            'amount': log.credit_amount,
                            'date': log.due_date.strftime("%A,%d %B, %Y")
                        }
                        message = setting_msg.value.format(**values)
                        print(devices)
                        if not devices:
                            print("No device found!!")
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


def credit_cycle_update():
    cycles = CreditCycle.objects.all()
    for cycle in cycles:
        date_yesterday = date.today() - timedelta(days=1)
        if date_yesterday == cycle.end_date.date():
            date_today = date.today()
            min_startdate = datetime.combine(date_today, time.min)
            cycle.start_date = min_startdate
            max_enddate = datetime.combine(
                date_today, time.max) + timedelta(days=cycle.credit_rule.time_period)
            cycle.end_date = max_enddate
            cycle.save()
            print("cycle updated for customer: ",
                  cycle.customer.id, "cycle id: ", cycle.id)
    print("Credit Cycle update successfully!!")


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
        filtered_list = CreditTxnFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(CustomerCreditTransactionReference,
                        self).get_context_data(**kwargs)
        context['filter_form'] = CreditTxnSearchFilter(self.request.GET)
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
            total_paid_amount = 0
            for trx in transactions:
                trx.payment_status = True
                trx.available += trx.paid_amount
                trx.available = round(trx.available, 2)
                total_paid_amount += trx.paid_amount
                trx.save()
            payment_ref.is_verified = True
            update_limit = CreditManagement.objects.get(
                customer=payment_ref.customer)
            update_limit.available += total_paid_amount
            update_limit.save()
        payment_ref.payment_status = status
        payment_ref.save()
        return HttpResponse("Successfully Updated")


def credit_cycle_generator():
    credit_management = CreditManagement.objects.all()
    for credit in credit_management:
        credit_cycle, created = CreditCycle.objects.get_or_create(
            customer_id=credit.customer_id)
        date_today = date.today()
        min_startdate = datetime.combine(date_today, time.min)
        max_enddate = datetime.combine(
            date_today, time.max) + timedelta(days=credit.credit_rule.time_period)
        credit_cycle.start_date = min_startdate
        credit_cycle.end_date = max_enddate
        credit_cycle.credit_rule_id = credit.credit_rule.id
        credit_cycle.save()
    print("DONE")
