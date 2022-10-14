from django.contrib.auth.decorators import permission_required
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
import uuid
from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import LocalizationMobileSettings
from wayrem_admin.forms import SettingsForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.utils.constants import *
from wayrem_admin.export import generate_excel
from django.urls import reverse_lazy
from wayrem_admin.filters.localizationmobile_filters import LocalizationMobileFilter
from django.views.generic import ListView
from wayrem_admin.forms.setting import SettingSearchFilter
import pandas as pd
import xlsxwriter
import io

class MobileLocalizationList(LoginPermissionCheckMixin, ListView):
    permission_required = 'settings.list'
    model = LocalizationMobileSettings
    template_name = "settings/localization/list.html"
    context_object_name = 'mobile_localization'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:settingslist')

    def get_queryset(self):
        qs = LocalizationMobileSettings.objects.all()
        filtered_list = LocalizationMobileFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(MobileLocalizationList,self).get_context_data(**kwargs)
        context['filter_form'] = SettingSearchFilter(self.request.GET)
        context['form'] = SettingsForm()
        return context

class MobileLocalizationExport(View):
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, **kwargs):
        qs = LocalizationMobileSettings.objects.values('localization_key', 'lang_en', 'lang_ar')
        query_set = qs
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
        filename = 'mobile_localization_lang.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

class MobileLocalizationImport(View):
    def get(self,request):
        return redirect('wayrem_admin:localization_list')

    def post(self,request):
        file = request.FILES["myFileInput"]
        if file is None:
            messages.error(request, "File is missing. Upload Again!")
            return redirect('wayrem_admin:localization_list')
        
        insert_list=['localization_key'	,'lang_en',	'lang_ar']
        df = pd.read_excel(file)
        df = df.where(pd.notnull(df), None)
        list_insert=[]
        for  index, row in df.iterrows():
            ins_dic={}
            for colinsert in insert_list:
                ins_dic[colinsert]=None
                if colinsert in row:
                    if row[colinsert] is not None:
                        ins_dic[colinsert]=row[colinsert]
                    else:
                        messages.error(request, "Cant insert empty  in field "+colinsert)
                        return redirect('wayrem_admin:localization_list')    
                else:
                    messages.error(request, "Missing Coloumn key. Please check the excel format by export.")
                    return redirect('wayrem_admin:localization_list')
            list_insert.append(ins_dic)
        
        LocalizationMobileSettings.truncate()
        for insert_mob_loc in list_insert:
            m2=LocalizationMobileSettings(**insert_mob_loc)
            m2.save()
        messages.success(request, "Mobile Localization update successfully")    
        return redirect('wayrem_admin:localization_list')
        
    