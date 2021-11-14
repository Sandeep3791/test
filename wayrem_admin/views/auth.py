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
from wayrem_admin.models import CustomUser, Otp
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from wayrem_admin.services import send_email
import random


class LoginView(View):
    template_name = "accounts/login.html"

    @method_decorator(anonymous(login_url='/dashboard/'))
    def get(self, request, format=None):
        return render(request, self.template_name)

    def post(self, request):
        print(".....................")
        print(request)
        username = request.POST['username']
        password = request.POST['password']

        user = CustomUser.objects.filter(username=username).first(
        )
        if user is None:
            messages.error(request, "User not found!")
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
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email Doesn't Exist!")
            return redirect('wayrem_admin:forgot-password')
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND, detail="Email doesn't exist!")
        else:
            no = random.randint(1000, 99999)
            to = email
            subject = 'Your Wayrem password reset request !'
            body = f'Your One time password is: <strong><em>{no}</em></strong>'
            send_email(to, subject, body)

            data1 = {"email": request.POST['email'], "otp": no}
            print(data1)
            user = Otp(email=email, otp=no)
            user.save()
            return render(request, 'reset-password.html', {'email': email})


class Reset_Password(View):
    # serializer_class = ResetSerializer

    def get(self, request):
        email = request.session.get('fpemail', None)
        return render(request, 'reset-password.html', {'email': email})

    def post(self, request, *args, **kwargs):
        email = request.session.get('fpemail')
        print(email)
        otp = request.POST.get('otp')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirm_password')
        if newpassword != confirmpassword:
            messages.error(request, "Password Doesn't Match!")
            return redirect('wayrem_admin:reset-password')
        print(newpassword)
        user = Otp.objects.filter(email=email, otp=otp).first()

        if user:
            print("Working")
            new_user = CustomUser.objects.get(email=email)
            new_user.password = make_password(newpassword)
            new_user.save()
            messages.success(request, "Password Changed Successfully!")
            return redirect('wayrem_admin:login')
        else:
            print("Not Working")
            messages.error(request, "OTP Invalid!")
            return redirect('wayrem_admin:reset-password')


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
