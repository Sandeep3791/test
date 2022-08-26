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
import xlsxwriter
import io
from django.db.models import F
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin

class AvailableExportView(View):
    def get(self, request, **kwargs):
        qs = Products.objects.annotate(Sku=F('SKU'), Name=F('name'), Brand=F('mfr_name'), Unit=F('weight_unit__unit_name'), Price=F(
            'price'), Quantity=F('quantity')).values('Sku', 'Name', 'Brand', 'Unit', 'Price', 'Quantity').filter(quantity__gt = 0)
        
        filtered_list = AvailableStockFilter(self.request.GET, queryset=qs)
        query_set = filtered_list.qs
        response = self.genrate_excel(query_set)
        return response

    def genrate_excel(self, query_set):
        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for row_number, query in enumerate(query_set):
            col_key = 0
            for key, values in query.items():
                if row_number == 0:
                    bold = workbook.add_format(
                        {'bold': True, 'font_color': 'white', 'bg_color': '#0d72ba'})
                    worksheet.set_row(row_number, 30)
                    worksheet.write(row_number, col_key, key, bold)
                    worksheet.set_column(row_number, col_key, 20)
                worksheet.write(row_number+1, col_key, values)
                col_key = col_key+1

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)
        filename = 'order_report.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

class AvailableStock(LoginPermissionCheckMixin,ListView):
    permission_required = 'availablestock.list_view'
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