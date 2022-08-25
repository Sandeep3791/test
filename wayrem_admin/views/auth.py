from django.utils.translation import ugettext_lazy as _
from wayrem_admin.forms import ChangePasswordForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.views import PasswordContextMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from wayrem_admin.decorators import anonymous
from django.contrib.auth import update_session_auth_hash
from wayrem_admin.forms.account import ResetPasswordForm
from wayrem_admin.models import User, Otp, EmailTemplateModel
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from wayrem_admin.services import send_email
import random
from wayrem_admin.models.users import Users


class LoginView(View):
    template_name = "accounts/login.html"

    @method_decorator(anonymous(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        return render(request, self.template_name)

    def post(self, request):
        print(".....................")
        print(request)
        username = request.POST['username']
        password = request.POST['password']

        user = Users.objects.filter(username=username).first(
        )
        if user is None:
            messages.error(request, "Invalid credentials. Please try again!")
            return redirect('wayrem_admin:login')
        if not check_password(password, user.password):
            messages.error(request, "Invalid credentials. Please try again!")
            return redirect('wayrem_admin:login')

        if not user.is_active:
            messages.error(request, "User is Blocked!")
            return redirect('wayrem_admin:login')

        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, "Logged in Successfully!")
        return redirect('wayrem_admin:dashboard')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('wayrem_admin:login')


class Forgot_Password(View):
    # serializer_class = OtpSerializer

    # @method_decorator(anonymous(login_url='wayrem_admin:dashboard'))
    def get(self, request):
        return render(request, 'forgot-password.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        request.session['fpemail'] = email
        user = Users.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email Doesn't Exist!")
            return redirect('wayrem_admin:forgot-password')
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND, detail="Email doesn't exist!")
        else:
            no = random.randint(1000, 99999)
            to = email
            obj = EmailTemplateModel.objects.filter(key='otp_user').first()
            values = {
                'user': user.username,
                'otp': no
            }
            subject = obj.subject
            body = obj.message_format.format(**values)
            send_email(to, subject, body)

            data1 = {"email": request.POST['email'], "otp": no}
            print(data1)
            user = Otp(email=email, otp=no)
            user.save()
            return redirect('wayrem_admin:reset-password')
            # return render(request, 'reset-password.html', {'email': email})


class Reset_Password(View):
    form = ResetPasswordForm

    def get(self, request):
        email = request.session.get('fpemail', None)
        form = self.form(initial={'email': email})
        return render(request, 'reset-password.html', {'email': email, 'form': form})

    def post(self, request, *args, **kwargs):
        email = request.session.get('fpemail')
        updated_request = request.POST.copy()
        updated_request.update({'email': email})
        form = self.form(updated_request)
        if form.is_valid():
            new_user = Users.objects.get(email=email)
            new_user.password = make_password(
                form.cleaned_data.get('new_password'))
            new_user.save()
            otp_delete = Otp.objects.filter(email=email)
            otp_delete.delete()
            messages.success(request, "Password Changed Successfully!")
            return redirect('wayrem_admin:login')
        else:
            return render(request, 'reset-password.html', {'form': form})


class Change_PasswordView(PasswordContextMixin, FormView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('wayrem_admin:dashboard')
    template_name = 'change-password.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed.")
        return super(FormView, self).form_valid(form)


def test(request):
    return render(request, "test.html")
