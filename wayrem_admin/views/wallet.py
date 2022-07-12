import base64
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from wayrem_admin.models import Settings
from wayrem_admin.models import Orders, Wallet
from wayrem_admin.models import Settings
from django.views.generic import ListView, DetailView
from wayrem_admin.forms import OrderStatusUpdatedForm, OrderAdvanceFilterForm, OrderStatusDetailForm, OrderUpdatedPaymentStatusForm, OrderStatusFilter
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.wallet_filters import WalletFilter
import datetime
import io
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
from django.db.models import Sum


class WalletList(ListView):
    login_url = 'wayrem_admin:root'
    model = Wallet
    template_name = "orders/wallet_list.html"
    context_object_name = 'wallet'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:walletlistcreate')

    def get_queryset(self):
        id=self.kwargs['id']
        qs = self.model.objects.filter(customer=id).order_by("-id")
        filtered_list = WalletFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(WalletList, self).get_context_data(**kwargs)
        id=self.kwargs['id']
        transaction_id=self.model.objects.values('transaction_type_id').annotate(total_sum=Sum('amount'))
        dr=0
        cr=0
        for tr in transaction_id:
            if tr['transaction_type_id'] == 1:
                dr=tr['total_sum']
            else:
                cr=tr['total_sum']
        total_amount=cr - dr
        if total_amount <= 0:
            total_amount=0
        context['total_amount']=total_amount
        return context


