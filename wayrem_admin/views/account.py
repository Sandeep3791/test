from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
from wayrem_admin.forms.account import UserSearchFilter
from wayrem_admin.utils.constants import *
from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SubAdminForm, ProfileUpdateForm, SubAdminUpdateForm, SupplierForm, SupplierUpdateForm
import string
import secrets
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import Users, EmailTemplateModel
from django.views import View
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.urls import reverse_lazy
from wayrem_admin.filters.user_filters import UserFilter


def user_excel(request):
    return generate_excel("users", "users")


def user_signup(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SubAdminForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                contact = form.cleaned_data['contact']
                role = form.cleaned_data['role']
                print(role)
                password = form.cleaned_data['password1']
                print(password)
                form.is_superuser = 0
                form.save()
                to = email
                obj = EmailTemplateModel.objects.filter(
                    key='user_register').first()
                # subject = 'Welcome to Wayrem'
                values = {
                    'username': username,
                    'password': password,
                    'email': email,
                }
                subject = obj.subject
                body = obj.message_format.format(**values)
                # body = f'Your credential for <strong> Wayrem </strong> are:\n <br> Username: <em>{username}</em>\n  <br> Password: <em>{password}</em>\n <br> Email: <em>{email}</em>\n'
                send_email(to, subject, body)
                # Role: {role}
                messages.success(request, 'User Created Successfully!!')
                return redirect('wayrem_admin:userlist')
        else:
            alphabet = string.ascii_letters + string.digits
            auto_password = ''.join(secrets.choice(alphabet) for i in range(8))
            form = SubAdminForm(
                initial={'password1': auto_password, 'password2': auto_password})
        return render(request, 'accounts/register.html', {"form": form})
    else:
        return redirect('wayrem_admin:dashboard')


class UsersList(LoginPermissionCheckMixin, ListView):
    permission_required = 'user_management.users_list'
    model = Users
    template_name = "users/list.html"
    context_object_name = 'userlist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:userlist')

    def get_queryset(self):
        qs = Users.objects.filter().exclude(is_superuser=True)
        filtered_list = UserFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(UsersList, self).get_context_data(**kwargs)
        context['filter_form'] = UserSearchFilter(self.request.GET)
        return context


def user_details(request, id=None):
    user = Users.objects.filter(id=id).first()
    return render(request, 'user_popup.html', {'userdata': user})


def update_user(request, id=None):
    print(id)
    user = Users.objects.get(id=id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        form = SubAdminUpdateForm(request.POST or None, instance=user)
        if form.is_valid():
            form.save()
            return redirect('wayrem_admin:userlist')
    else:
        form = SubAdminUpdateForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'id': user.id})


@login_required(login_url='wayrem_admin:root')
def update_profile(request, *args, **kwargs):
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = Users.objects.get(username=request.user.username)

        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            print("FORM")

        # .cleaned_data['recipients']
            email = form.cleaned_data['email']
            fname = form.cleaned_data['first_name']
            lname = form.cleaned_data['last_name']
            contact = form.cleaned_data['contact']
            gender = form.cleaned_data['gender']
            dob = form.cleaned_data['dob']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            zip_code = form.cleaned_data['zip_code']
            user = Users.objects.get(username=request.user.username)
            user.email = email
            user.first_name = fname
            user.last_name = lname
            user.contact = contact
            user.gender = gender
            user.dob = dob
            user.address = address
            user.city = city
            user.zip_code = zip_code
            user.save()
            print("Here")
            return redirect('wayrem_admin:updateprofile')
    user = Users.objects.get(username=request.user.username)
    form = ProfileUpdateForm(instance=user)
    return render(request, 'settings.html', {'form': form})


class DeleteUser(LoginPermissionCheckMixin, View):
    permission_required = 'user_management.delete_user'

    def post(self, request):
        userid = request.POST.get('userid')
        user = Users.objects.get(pk=userid)
        user.delete()
        return redirect('wayrem_admin:userlist')


# Active/Block
class Active_BlockUser(LoginPermissionCheckMixin, View):
    permission_required = 'user_management.user_activate'

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, id):
        user = Users.objects.get(pk=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('wayrem_admin:userlist')
