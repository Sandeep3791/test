from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SubAdminForm, ProfileUpdateForm, SubAdminUpdateForm, SupplierRegisterForm, SupplierRegisterUpdateForm
import string
import secrets
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_pdf, generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import CustomUser, SupplierRegister
from django.views import View


def user_excel(request):
    return generate_excel("custom_user", "users")


def user_pdf(request):
    query = 'SELECT username, first_name, last_name, is_active, date_joined, email, contact,  dob, gender, address, city, zip_code FROM custom_user'
    template = "pdf_user.html"
    file = "users.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


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

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        userlist = CustomUser.objects.all()
        return render(request, self.template_name, {"userlist": userlist})


def user_details(request, id=None):
    user = CustomUser.objects.filter(id=id).first()
    return render(request, 'user_popup.html', {'userdata': user})


def update_user(request, id=None):
    print(id)
    user = CustomUser.objects.get(id=id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        form = SubAdminUpdateForm(request.POST or None, instance=user)
        if form.is_valid():
            form.save()
            return redirect('wayrem_admin:userlist')
    else:
        form = SubAdminUpdateForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'id': user.id})


@login_required(login_url='/')
def update_profile(request, *args, **kwargs):
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = CustomUser.objects.get(username=request.user.username)

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
            user = CustomUser.objects.get(username=request.user.username)
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
    user = CustomUser.objects.get(username=request.user.username)
    form = ProfileUpdateForm(instance=user)
    return render(request, 'settings.html', {'form': form})


class DeleteUser(View):
    def post(self, request):
        userid = request.POST.get('userid')
        user = CustomUser.objects.get(pk=userid)
        user.delete()
        return redirect('wayrem_admin:userlist')


# Active/Block
class Active_BlockUser(View):
    @method_decorator(login_required(login_url='/'))
    def get(self, request, id):
        user = CustomUser.objects.get(pk=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('wayrem_admin:userlist')
