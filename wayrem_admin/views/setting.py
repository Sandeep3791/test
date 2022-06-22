from django.contrib.auth.decorators import permission_required
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
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
from wayrem_admin.utils.constants import *
from wayrem_admin.export import generate_excel
from django.urls import reverse_lazy
from wayrem_admin.filters.settings_filters import SettingsFilter
from django.views.generic import ListView
from wayrem_admin.forms.setting import SettingSearchFilter


def settings_excel(request):
    return generate_excel("settings", "settings")


# class SettingList(View):
#     template_name = "settinglist.html"
#     form = SettingsForm()

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     def get(self, request, format=None):
#         userlist = Settings.objects.all()
#         paginator = Paginator(userlist, RECORDS_PER_PAGE)
#         page = request.GET.get('page')
#         try:
#             slist = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             slist = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             slist = paginator.page(paginator.num_pages)
#         return render(request, self.template_name, {"userlist": slist, "form": self.form})

#     def post(self, request):
#         self.form = SettingsForm(request.POST)
#         if self.form.is_valid():
#             self.form.save()
#             return redirect('wayrem_admin:settings')
#         else:
#             userlist = Settings.objects.all()
#             return render(request, self.template_name, {"userlist": userlist, "form": self.form})

class SettingList(LoginPermissionCheckMixin, ListView):
    permission_required = 'settings.list'
    model = Settings
    template_name = "settings/list.html"
    context_object_name = 'userlist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:settingslist')

    def get_queryset(self):
        qs = Settings.objects.all()
        filtered_list = SettingsFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(SettingList, self).get_context_data(**kwargs)
        context['filter_form'] = SettingSearchFilter(self.request.GET)
        context['form'] = SettingsForm()
        return context


@permission_required('settings.update', raise_exception=True)
def update_settings(request, id=None):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        obj = Settings.objects.filter(id=id).first()
        obj.display_name = request.POST.get('display_name')
        obj.value = request.POST.get('value')
        obj.save()
        return redirect('wayrem_admin:settingslist')
    else:
        return redirect('wayrem_admin:settingslist')


class CreateSetting(LoginPermissionCheckMixin, View):
    permission_required = 'settings.create'
    template_name = "settings/list.html"
    form = SettingsForm()

    def post(self, request):
        self.form = SettingsForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            return redirect('wayrem_admin:settingslist')
        else:
            userlist = Settings.objects.all()
            return render(request, self.template_name, {"userlist": userlist, "form": self.form})
