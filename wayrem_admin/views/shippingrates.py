from django.shortcuts import render, redirect
from django.contrib import messages

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from wayrem_admin.forms import ShippingRatesForm, ShippingRatesFilterForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.export import generate_excel
from wayrem_admin.models import ShippingRates
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.shippingrates_filters import ShippingRatesFilter
from django.db.models import Sum, Case, CharField, Value, When
from django.db.models import F
import datetime
import xlsxwriter
import io
# pdf export
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models.functions import Cast
from django.db.models.fields import DateField


class ShippingRatesList(LoginRequiredMixin, ListView):
    model = ShippingRates
    template_name = "shippingrates/list.html"
    context_object_name = 'shippingrates'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:shippingrates')

    def dispatch(self, *args, **kwargs):
        return super(ShippingRatesList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = ShippingRates.objects.filter().order_by("from_dest")
        filtered_list = ShippingRatesFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(ShippingRatesList, self).get_context_data(**kwargs)
        context['filter_form'] = ShippingRatesFilterForm(self.request.GET)
        return context


class ShippingRatesCreate(LoginRequiredMixin, CreateView):
    model = ShippingRates
    form_class = ShippingRatesForm
    template_name = 'shippingrates/add.html'
    success_url = reverse_lazy('wayrem_admin:shippingrates')

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(ShippingRatesCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form = form.save(commit=False)
        get_all_shipping_rates = self.model.objects.filter()
        list_exist = []
        for get_all_shipping_rate in get_all_shipping_rates:
            from_dest = int(get_all_shipping_rate.from_dest)
            to_dest = int(get_all_shipping_rate.to_dest)+1
            x = range(from_dest, to_dest)
            for n in x:
                list_exist.append(n)

        form_from_dest = int(form.from_dest)
        form_to_dest = int(form.to_dest)
        if (form_from_dest in list_exist) or (form_to_dest in list_exist):
            messages.error(self.request, 'Please dont overlap KMs.')
        else:
            form.save()
            messages.success(self.request, 'Shipping Rate added successfully.')
        return HttpResponseRedirect(self.success_url)


class ShippingRatesUpdate(LoginRequiredMixin, UpdateView):
    model = ShippingRates
    form_class = ShippingRatesForm
    template_name = 'shippingrates/update.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('wayrem_admin:shippingrates')

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def dispatch(self, *args, **kwargs):
        return super(ShippingRatesUpdate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shippingratesid = self.kwargs['pk']
        context['shipping_rate_pk'] = shippingratesid
        return context

    def form_valid(self, form):
        form = form.save(commit=False)
        get_id = self.get_object().id

        get_all_shipping_rates = self.model.objects.filter().exclude(id=get_id)
        list_exist = []
        for get_all_shipping_rate in get_all_shipping_rates:
            from_dest = int(get_all_shipping_rate.from_dest)
            to_dest = int(get_all_shipping_rate.to_dest)+1
            x = range(from_dest, to_dest)
            for n in x:
                list_exist.append(n)

        form_from_dest = int(form.from_dest)
        form_to_dest = int(form.to_dest)
        if (form_from_dest in list_exist) or (form_to_dest in list_exist):
            messages.error(self.request, 'Please dont overlap KMs.')
        else:
            form.save()
            messages.success(self.request, 'Shipping Rate added successfully.')

        return HttpResponseRedirect(self.success_url)
