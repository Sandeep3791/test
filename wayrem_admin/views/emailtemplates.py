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
from wayrem_admin.models import EmailTemplateModel
from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import ListView
from wayrem_admin.forms import EmailtemplatesForm,EmailtemplatesViewForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.decorators import role_required

class EmailtemplatesList(View):
    template_name = "emailtemplate/list.html"
    form = SettingsForm()
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Email Template View'))
    def get(self, request, format=None):
        userlist = EmailTemplateModel.objects.all()
        paginator = Paginator(userlist,1)
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

class EmailtemplatesCreate(CreateView):
    model=EmailTemplateModel
    form_class = EmailtemplatesForm
    template_name = 'emailtemplate/add.html'
    success_url = reverse_lazy('wayrem_admin:emailtemplates')
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Email Template Add'))
    def dispatch(self, *args, **kwargs):
        return super(EmailtemplatesCreate, self).dispatch(*args, **kwargs)
    
class EmailtemplatesUpdate(UpdateView):
    model=EmailTemplateModel
    form_class = EmailtemplatesForm
    template_name = 'emailtemplate/update.html'
    pk_url_kwarg = 'emailtemplate_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Email Template Edit'))
    def dispatch(self, *args, **kwargs):
        return super(EmailtemplatesUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
            return reverse_lazy('wayrem_admin:updateemailtemplates', kwargs={'emailtemplate_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emailtemplate_pk=self.kwargs['emailtemplate_pk']
        context['emailtemplate_pk'] =emailtemplate_pk
        return context

class EmailtemplatesView(UpdateView):
    model=EmailTemplateModel
    form_class = EmailtemplatesViewForm
    template_name = 'emailtemplate/view.html'
    pk_url_kwarg = 'emailtemplate_pk'
    
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Email Template View'))
    def dispatch(self, *args, **kwargs):
        return super(EmailtemplatesView, self).dispatch(*args, **kwargs)
        
    def get_success_url(self):
            return reverse_lazy('wayrem_admin:viewemailtemplates', kwargs={'emailtemplate_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emailtemplate_pk=self.kwargs['emailtemplate_pk']
        context['emailtemplate_pk'] =emailtemplate_pk
        return context