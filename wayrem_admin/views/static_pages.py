from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from wayrem_admin.models import Settings, StaticPages
from wayrem_admin.forms import SettingsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import CreateView, UpdateView
from wayrem_admin.forms import StaticpagesForm, StaticpagesViewForm
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from django.urls import reverse_lazy
from wayrem_admin.filters.static_pages import StaticPageFilter
from django.views.generic import ListView
from wayrem_admin.forms.static_pages import StaticPageSearchFilter


# class StaticpagesList(View):
#     template_name = "static_pages/list.html"
#     form = SettingsForm()

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     def get(self, request, format=None):
#         userlist = StaticPages.objects.all()
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
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin


class StaticpagesList(LoginPermissionCheckMixin, ListView):
    permission_required = 'static_page.list'
    model = StaticPages
    template_name = "static_pages/list.html"
    context_object_name = 'userlist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:staticpages')

    def get_queryset(self):
        qs = StaticPages.objects.all()
        filtered_list = StaticPageFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(StaticpagesList, self).get_context_data(**kwargs)
        context['filter_form'] = StaticPageSearchFilter(self.request.GET)
        return context


class StaticpagesCreate(LoginPermissionCheckMixin, CreateView):
    permission_required = 'static_page.create'
    model = StaticPages
    form_class = StaticpagesForm
    template_name = 'static_pages/add.html'
    success_url = reverse_lazy('wayrem_admin:staticpages')


class StaticpagesUpdate(LoginPermissionCheckMixin, UpdateView):
    permission_required = 'static_page.edit'
    model = StaticPages
    form_class = StaticpagesForm
    template_name = 'static_pages/update.html'
    pk_url_kwarg = 'static_pages_pk'

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:updatestaticpages', kwargs={'static_pages_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        static_pages_pk = self.kwargs['static_pages_pk']
        context['static_pages_pk'] = static_pages_pk
        return context


class StaticpagesView(LoginPermissionCheckMixin, UpdateView):
    permission_required = 'static_page.view'
    model = StaticPages
    form_class = StaticpagesViewForm
    template_name = 'static_pages/view.html'
    pk_url_kwarg = 'static_pages_pk'

    def get_success_url(self):
        return reverse_lazy('wayrem_admin:viewemailtemplates', kwargs={'static_pages_pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        static_pages_pk = self.kwargs['static_pages_pk']
        context['static_pages_pk'] = static_pages_pk
        return context


class DeleteStaticpages(LoginPermissionCheckMixin, View):
    permission_required = 'static_page.delete'

    def post(self, request):
        pageid = request.POST.get('pageid')
        user = StaticPages.objects.get(pk=pageid)
        user.delete()
        return redirect('wayrem_admin:staticpages')


@permission_required('static_page.view', raise_exception=True)
def staticpages_view(request, url):
    data = StaticPages.objects.filter(slug=url).first()
    context = {
        "title": data.page_title,
        "description": data.description
    }
    return render(request, "static_pages/view_template.html", context)
