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


def settings_excel(request):
    return generate_excel("settings", "settings")


class SettingList(View):
    template_name = "settinglist.html"
    form = SettingsForm()

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        userlist = Settings.objects.all()
        paginator = Paginator(userlist, 5)
        page = request.GET.get('page')
        try:
            slist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            slist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            slist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"userlist": slist, "form": self.form})

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
