from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from wayrem_admin.models import Settings
from wayrem_admin.models_orders import Orders, OrderDetails, StatusMaster, OrderDeliveryLogs, OrderTransactions
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.models.BankModels import Banks
from wayrem_admin.forms.bank import BankUpdatedForm,BankFilterForm,BankViewForm
from wayrem_admin.filters.bank_filters import BankFilter

class BanksList(LoginRequiredMixin, ListView):
    login_url = 'wayrem_admin:root'
    model = Banks
    template_name = "bank/list.html"
    context_object_name = 'banks'
    paginate_by = 25
    success_url = reverse_lazy('wayrem_admin:banklist')

    def get_queryset(self):
        qs = Banks.objects.filter(is_deleted=0)
        filtered_list = BankFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(BanksList, self).get_context_data(**kwargs)
        context['filter_form'] = BankFilterForm(self.request.GET)
        return context
class BankView(LoginRequiredMixin,UpdateView):
    
    login_url = 'wayrem_admin:root'
    model = Banks
    form_class = BankViewForm
    template_name = "bank/view.html"
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_pk = self.kwargs['id']
        context['id_pk'] = id_pk
        return context
    
    def get_success_url(self):
          # if you are passing 'pk' from 'urls' to 'DeleteView' for company
          # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
          bank_id=self.kwargs['id']
          return reverse_lazy('wayrem_admin:updatebank', kwargs={'id': bank_id})
class BanksUpdated(LoginRequiredMixin, UpdateView):
    login_url = 'wayrem_admin:root'
    model = Banks
    form_class = BankUpdatedForm
    template_name = "bank/update.html"
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_pk = self.kwargs['id']
        context['id_pk'] = id_pk
        return context
    
    def get_success_url(self):
          # if you are passing 'pk' from 'urls' to 'DeleteView' for company
          # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
          bank_id=self.kwargs['id']
          return reverse_lazy('wayrem_admin:updatebank', kwargs={'id': bank_id})

class BanksCreate(CreateView):
    model = Banks
    form_class = BankUpdatedForm
    template_name = 'bank/add.html'
    success_url = reverse_lazy('wayrem_admin:banklist')

class BankUpdateStatusView(View):
    def get(self,request, id):
        Banks.objects.filter(id=1).update(is_deleted=1)
        return HttpResponse(1)