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
from wayrem_admin.models import Inventory
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from wayrem_admin.forms import InventoryForm,InventoryViewForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Q
from wayrem_admin.decorators import role_required
from wayrem_admin.utils.constants import * 

class InventoriesList(View):
    template_name = "inventories/list.html"
    form = SettingsForm()
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Inventory View'))
    def get(self, request, format=None):
        inventories = Inventory.objects.all()
        q = request.GET.get('q') if request.GET.get('q') != None else '' 
        if q != None:
            inventories = inventories.filter(Q(product__SKU__icontains=q) )
            #inventories = inventories.filter(Q(product__SKU__icontains=q) | Q(inventory_type__icontains=q))
        paginator = Paginator(inventories,RECORDS_PER_PAGE)
        page = request.GET.get('page')
        try:
            slist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            slist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            slist = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {"inventories": slist, 'q':q, "form": self.form})

class InventoryCreate(CreateView):
    model=Inventory
    form_class = InventoryForm
    template_name = 'inventories/add.html'
    success_url = reverse_lazy('wayrem_admin:inventories')
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Inventory Add'))
    def dispatch(self, *args, **kwargs):
        return super(InventoryCreate, self).dispatch(*args, **kwargs)
    
class InventoryUpdate(UpdateView):
    model=Inventory
    form_class = InventoryForm
    template_name = 'inventories/update.html'
    pk_url_kwarg = 'inventory_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Inventory Edit'))
    def dispatch(self, *args, **kwargs):
        return super(InventoryUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
            return reverse_lazy('wayrem_admin:update_inventory', kwargs={'inventory_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_pk=self.kwargs['inventory_pk']
        context['inventory_pk'] =inventory_pk
        return context

class InventoryView(UpdateView):
    model=Inventory
    form_class = InventoryViewForm
    template_name = 'inventories/view.html'
    pk_url_kwarg = 'inventory_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Inventory Edit'))
    def dispatch(self, *args, **kwargs):
        return super(InventoryView, self).dispatch(*args, **kwargs)
        
    def get_success_url(self):
            return reverse_lazy('wayrem_admin:view_inventory', kwargs={'inventory_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_pk=self.kwargs['inventory_pk']
        context['inventory_pk'] =inventory_pk
        return context