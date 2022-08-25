from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from wayrem_admin.utils.constants import *
from wayrem_admin.models import Products
from django.urls import reverse_lazy
from wayrem_admin.filters.available_stock_filters import AvailableStockFilter

class AvailableStock(ListView):
    model = Products
    template_name = "available_stock/list.html"
    context_object_name = 'products'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:orderlist')

    def get_queryset(self):
        qs = self.model.objects.filter(quantity__gt = 0).order_by("-id")
        filtered_list = AvailableStockFilter(self.request.GET, queryset=qs)
        return filtered_list.qs
        
    def get_context_data(self, **kwargs):
        context = super(AvailableStock, self).get_context_data(**kwargs)
        if self.request.GET.get('search') is None:
            context['search'] = ""
        else:
            context['search'] = self.request.GET.get('search')
        return context