from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SubAdminForm, ProfileUpdateForm, SubAdminUpdateForm, SupplierForm, SupplierUpdateForm
import string
import secrets
from wayrem_admin.decorators import role_required
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_pdf, generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import User, Supplier
from django.views import View
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def user_excel(request):
    return generate_excel("users", "users")


def user_pdf(request):
    query = 'SELECT username, first_name, last_name, is_active, date_joined, email, contact,  dob, gender, address, city, zip_code FROM users'
    template = "pdf_user.html"
    file = "users.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


@role_required('User Add')
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
                form.save()
                to = email
                subject = 'Welcome to Wayrem'
                body = f'Your credential for <strong> Wayrem </strong> are:\n <br> Username: <em>{username}</em>\n  <br> Password: <em>{password}</em>\n <br> Email: <em>{email}</em>\n'
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


class UsersList(View):
    template_name = "userlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('User View'))
    def get(self, request, format=None):
        userlist = User.objects.all()
        paginator = Paginator(userlist, 25)
        page = request.GET.get('page')
        try:
            ulist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            ulist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ulist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"userlist": ulist})


@role_required('User View')
def user_details(request, id=None):
    user = User.objects.filter(id=id).first()
    return render(request, 'user_popup.html', {'userdata': user})


@role_required('User Edit')
def update_user(request, id=None):
    print(id)
    user = User.objects.get(id=id)
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
        user = User.objects.get(username=request.user.username)

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
            user = User.objects.get(username=request.user.username)
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
    user = User.objects.get(username=request.user.username)
    form = ProfileUpdateForm(instance=user)
    return render(request, 'settings.html', {'form': form})


class DeleteUser(View):

    @method_decorator(role_required('User Delete'))
    def post(self, request):
        userid = request.POST.get('userid')
        user = User.objects.get(pk=userid)
        user.delete()
        return redirect('wayrem_admin:userlist')


# Active/Block
class Active_BlockUser(View):
    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('User Edit'))
    def get(self, request, id):
        user = User.objects.get(pk=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('wayrem_admin:userlist')
