import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Settings
from wayrem_admin.forms import SettingsForm


from wayrem_admin.export import generate_pdf, generate_excel


def settings_excel(request):
    return generate_excel("settings", "settings")


def pdf_settings(request):
    query = 'SELECT id, key, display_name, value, details, type, order FROM settings'
    template = "pdf_settings.html"
    file = "settings.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


class SettingList(View):
    template_name = "settinglist.html"
    form = SettingsForm()

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        userlist = Settings.objects.all()
        return render(request, self.template_name, {"userlist": userlist, "form": self.form})

    def post(self, request):
        self.form = SettingsForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            return redirect('wayrem_admin:settings')
        else:
            userlist = Settings.objects.all()
            return render(request, self.template_name, {"userlist": userlist, "form": self.form})


def update_settings(request, id=None):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        obj = Settings.objects.filter(id=id).first()
        obj.display_name = request.POST.get('display_name')
        obj.value = request.POST.get('value')
        obj.save()
        return redirect('wayrem_admin:settings')
    else:
        return redirect('wayrem_admin:settings')
