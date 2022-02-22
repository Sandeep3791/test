from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from grpc import Status
from wayrem_admin.models import Settings, StaticPages
from wayrem_admin.forms import SettingsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import CreateView, UpdateView
from wayrem_admin.forms import StaticpagesForm, StaticpagesViewForm
from django.urls import reverse_lazy
from wayrem_admin.decorators import role_required
from wayrem_admin.utils.constants import *


class StaticpagesList(View):
    template_name = "static_pages/list.html"
    form = SettingsForm()

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Static Pages View'))
    def get(self, request, format=None):
        userlist = StaticPages.objects.all()
        paginator = Paginator(userlist, RECORDS_PER_PAGE)
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


class StaticpagesCreate(CreateView):
    model = StaticPages
    form_class = StaticpagesForm
    template_name = 'static_pages/add.html'
    success_url = reverse_lazy('wayrem_admin:staticpages')

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Static Pages Add'))
    def dispatch(self, *args, **kwargs):
        return super(StaticpagesCreate, self).dispatch(*args, **kwargs)


class StaticpagesUpdate(UpdateView):
    model = StaticPages
    form_class = StaticpagesForm
    template_name = 'static_pages/update.html'
    pk_url_kwarg = 'static_pages_pk'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Static Pages Edit'))
    def dispatch(self, *args, **kwargs):
        return super(StaticpagesUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:updatestaticpages', kwargs={'static_pages_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        static_pages_pk = self.kwargs['static_pages_pk']
        context['static_pages_pk'] = static_pages_pk
        return context


class StaticpagesView(UpdateView):
    model = StaticPages
    form_class = StaticpagesViewForm
    template_name = 'static_pages/view.html'
    pk_url_kwarg = 'static_pages_pk'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Static Pages View'))
    def dispatch(self, *args, **kwargs):
        return super(StaticpagesView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:viewemailtemplates', kwargs={'static_pages_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        static_pages_pk = self.kwargs['static_pages_pk']
        context['static_pages_pk'] = static_pages_pk
        return context


class DeleteStaticpages(View):

    @method_decorator(role_required('Static Pages Delete'))
    def post(self, request):
        pageid = request.POST.get('pageid')
        user = StaticPages.objects.get(pk=pageid)
        user.delete()
        return redirect('wayrem_admin:staticpages')


def staticpages_view(request, url):
    data = StaticPages.objects.filter(slug=url).first()
    context = {
        "title": data.page_title,
        "description": data.description
    }
    return render(request, "static_pages/view_template.html", context)
