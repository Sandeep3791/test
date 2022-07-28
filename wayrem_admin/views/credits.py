from django.db.models import Sum
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


class CreditCreate(LoginPermissionCheckMixin, CreateView):
    permission_required = 'credits.settings_add'
    model = CreditSettings
    form_class = CreditsForm
    template_name = 'credits/add.html'
    success_url = reverse_lazy('wayrem_admin:customerslist')

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
            assign_credit = CreditManagement(
                customer=id, credit_rule=credit, used=0, available=15000)
            assign_credit.save()
        return redirect('wayrem_admin:customerslist')


@permission_required('credits.assign_customer', raise_exception=True)
def creditAssign(request, id=None):
    try:
        existing_credit_check = CreditManagement.objects.get(
            customer_id=id)
        existing_credit = existing_credit_check
    except:
        existing_credit = None
    if request.method == "POST":
        form = CreditsAssignForm(request.POST)
        if form.is_valid():
            credit = form.cleaned_data.get("credit")
            available_credit = CreditSettings.objects.get(id=credit)
            if existing_credit:
                existing_credit.credit_rule_id = available_credit
                existing_credit.used = 0
                existing_credit.available = available_credit.credit_amount
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
        self.total_credit = qs.aggregate(
            total=Sum('credit_amount'))['total'] or 0
        self.total_debit = qs.aggregate(total=Sum('paid_amount'))['total'] or 0
        return qs

    def get_context_data(self, **kwargs):
        context = super(CustomerCreditTransactionLogs,
                        self).get_context_data(**kwargs)
        context['customer'] = get_object_or_404(
            Customer, id=self.kwargs['customer_id'])
        context['total_credit'] = self.total_credit
        context['total_debit'] = self.total_debit
        return context


def credit_reminder():
    credit_management = CreditManagement.objects.all()
    for customer in credit_management:
        credit_logs = CreditTransactionLogs.objects.filter()
