import base64
from wayrem_admin.utils.constants import *
from django.contrib import messages
from wayrem import settings
import os
from wsgiref.util import FileWrapper
from io import BytesIO
import codecs
from django.views import View
from wayrem_admin.models import Invoice
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from wayrem_admin.filters.supplier_invoice import SupplierInvoiceFilter
from django.views.generic import ListView
from wayrem_admin.forms.supplier import SupplierInvoiceSearchFilter


# class InvoiceList(View):
#     template_name = "invoicelist.html"

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     def get(self, request, format=None):
#         userlist = Invoice.objects.all()
#         paginator = Paginator(userlist, 5)
#         page = request.GET.get('page')
#         try:
#             ulist = paginator.page(page)
#         except PageNotAnInteger:
#             ulist = paginator.page(1)
#         except EmptyPage:
#             ulist = paginator.page(paginator.num_pages)
#         return render(request, self.template_name, {"userlist": ulist})



class InvoiceList(ListView):
    model = Invoice
    template_name = "supplier_invoice/list.html"
    context_object_name = 'userlist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:invoicelist')

    def get_queryset(self):
        qs = Invoice.objects.all()
        filtered_list = SupplierInvoiceFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(InvoiceList, self).get_context_data(**kwargs)
        context['filter_form'] = SupplierInvoiceSearchFilter(self.request.GET)
        return context



class DownloadInvoice(View):
    def get(self, request):
        try:
            number = request.GET.get('invoice_no')
            invoice = number
            # invoice="INV/26112021/0001"
            contents = Invoice.objects.get(invoice_no=invoice)
            filename = contents.file.url.split('/')[-1]
            response = HttpResponse(
                contents.file, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; attachment; filename=%s' % filename

            return response
        except:
            messages.error(request, "Something went wrong!")
            return redirect('wayrem_admin:invoicelist')


class DownloadInvoicePO(View):
    def get(self, request):
        try:
            number = request.GET.get('poName')
            # invoice="INV/26112021/0001"
            contents = Invoice.objects.get(po_name=number)
            filename = contents.file.url.split('/')[-1]
            response = HttpResponse(
                contents.file, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; attachment; filename=%s' % filename

            return response
        except:
            messages.error(request, "Something went wrong!")
            return redirect('wayrem_admin:polist')