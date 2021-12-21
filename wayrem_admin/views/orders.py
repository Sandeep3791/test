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
from wayrem_admin.models_orders import Orders,OrderDetails
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from wayrem_admin.forms import EmailtemplatesForm,EmailtemplatesViewForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.decorators import role_required

class OrdersList(ListView):
    model=Orders
    template_name = "orders/list.html"
    context_object_name = 'orders'
    paginate_by = 1
    success_url = reverse_lazy('wayrem_admin:orderlist')