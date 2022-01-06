import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Settings
from wayrem_admin.forms import SettingsForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.export import generate_excel
from wayrem_admin.models import Warehouse
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from wayrem_admin.forms import WarehouseForm, WarehouseViewForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Q
from wayrem_admin.decorators import role_required
from wayrem_admin.utils.constants import * 

class WarehouseList(View):
    template_name = "warehouses/list.html"
    form = SettingsForm()
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Warehouse View'))
    def get(self, request, format=None):
        warehouses = Warehouse.objects.all()
        q = request.GET.get('q') if request.GET.get('q') != None else '' 
        if q != None:
            warehouses = warehouses.filter(code_name__icontains=q)
        paginator = Paginator(warehouses,RECORDS_PER_PAGE)
        page = request.GET.get('page')
        try:
            slist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            slist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            slist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"warehouses": slist, 'q': q, "form": self.form})

class WarehouseCreate(CreateView):
    model=Warehouse
    form_class = WarehouseForm
    template_name = 'warehouses/add.html'
    success_url = reverse_lazy('wayrem_admin:warehouses')
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Warehouse Add'))
    def dispatch(self, *args, **kwargs):
        return super(WarehouseCreate, self).dispatch(*args, **kwargs)
    
class WarehouseUpdate(UpdateView):
    model=Warehouse
    form_class = WarehouseForm
    template_name = 'warehouses/update.html'
    pk_url_kwarg = 'warehouse_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Warehouse Edit'))
    def dispatch(self, *args, **kwargs):
        return super(WarehouseUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
            return reverse_lazy('wayrem_admin:update_warehouse', kwargs={'warehouse_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_pk=self.kwargs['warehouse_pk']
        context['warehouse_pk'] =warehouse_pk
        return context

class WarehouseView(UpdateView):
    model=Warehouse
    form_class = WarehouseForm
    template_name = 'warehouses/view.html'
    pk_url_kwarg = 'warehouse_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Warehouse View'))
    def dispatch(self, *args, **kwargs):
        return super(WarehouseView, self).dispatch(*args, **kwargs)
        
    def get_success_url(self):
            return reverse_lazy('wayrem_admin:view_warehouse', kwargs={'warehouse_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_pk=self.kwargs['warehouse_pk']
        context['warehouse_pk'] =warehouse_pk
        return context