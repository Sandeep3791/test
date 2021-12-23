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
from wayrem_admin.models_orders import Orders,OrderDetails,OrderStatus
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from wayrem_admin.forms import OrderStatusUpdatedForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.decorators import role_required
from wayrem_admin.utils.constants import * 

class OrdersList(ListView):
    model=Orders
    template_name = "orders/list.html"
    context_object_name = 'orders'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:orderlist')


class OrderStatusUpdated(UpdateView):
    model = Orders
    form_class = OrderStatusUpdatedForm
    template_name = "orders/update_order_status.html"        
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_pk=self.kwargs['id']
        context['id_pk'] =id_pk
        return context

    def form_valid(self,form):
        # This method is called when valid form data has been POSTed. 
        obj = form.save(commit=False) 
        status_id=int(self.request.POST.get('status'))
        obj.status = OrderStatus.objects.get(id=status_id)
        obj.save()
        return HttpResponse("kp")

    def form_invalid(self, form):        
        return HttpResponse("kp")

    def post(self,request, *args, **kwargs):
        get_id = self.get_object().id
        status_id=int(self.request.POST.get('status'))
        obj_stat_instance = OrderStatus.objects.get(id=status_id)
        Orders.objects.filter(id=get_id).update(status=obj_stat_instance)
        #messages.success(self.request, 'Order status Updated!')
        return HttpResponse(obj_stat_instance.name)

class OrderInvoiceView(View):
    model = Orders
    template_name = "orders/update_order_status.html"

class OrderUpdateView(UpdateView):
    model = Orders
    form_class = OrderStatusUpdatedForm
    template_name = "orders/update_order_status.html"        
    pk_url_kwarg = 'id'