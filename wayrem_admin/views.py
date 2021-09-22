from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from .serializers import OtpSerializer, RoleSerializer, CustomRegisterSerializer, ResetSerializer
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
# from fastapi import HTTPException, status
from django.contrib.auth.hashers import make_password
from datetime import *
import jwt
import logging
import random
import smtplib
from django.http.response import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
logger = logging.getLogger(__name__)


@login_required(login_url='/')
def dashboard(request):
    return render(request, 'dashboard.html')


class LoginView(APIView):
    template_name = "accounts/login.html"

    def get(self, request, format=None):
        return render(request, self.template_name)

    def post(self, request):
        print(".....................")
        print(request)
        print(request.data)
        username = request.data['username']
        password = request.data['password']
        # print(username)
        # print(password)

        user = CustomUser.objects.filter(username=username).first(
        )
        if user is None:
            # raise AuthenticationFailed("User Not Found!")
            # return JsonResponse({"error": "User Not Found!"})
            messages.error(request, "User not found!!")
            return redirect('/')

        if not check_password(password, user.password):
            messages.error(request, "Incorrect Password!!")
            return redirect('/')
            # raise AuthenticationFailed("incorrect Password!")

        if not user.is_active:
            messages.error(request, "User is Blocked!!")
            return redirect('/')
            # return JsonResponse({"error": "User is Blocked"})

        user = authenticate(username=username, password=password)

        payload = {
            'id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret',
                           algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        print(response.cookies)
        response.data = {
            'jwt': token
        }
        login(request, user)
        messages.success(request, "Logged in Successfully!!")
        return redirect('/dashboard/')


def register(request):
    return render(request, 'accounts/register.html', )


class CustomRegisterAPI(generics.GenericAPIView):
    serializer_class = CustomRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        pwd = request.data.get('password')
        print(pwd)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(pwd)

        gmail_user = 'pankajspsq@gmail.com'
        gmail_password = 'Pankaj@05'

        sent_from = gmail_user
        to = user.email
        subject = 'Welcome to Wayrem'
        body = f'Your credential for wayrem are:\n username: {user.username} \n Email_id: {user.email} \n Password: {pwd} \n Role: {user.role}'
        print(pwd)
        email_text = f"From:{sent_from},To:{to} Subject: {subject}  {body}"
        # email_text = """\
        # From: %s
        # To: %s
        # Subject: %s
        # %s
        # """ % (sent_from, ", ".join(to), subject, body)

        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            print("Email sent successfully!")
        except Exception as ex:
            print("Something went wrong….", ex)
        messages.success(request, "Sub-Admin Created Successfully!!")
        return render(request, 'dashboard.html')
        # return Response({
        #     "user": Custom_userSerializer(user, context=self.get_serializer_context()).data,
        # })


class OtpApi(generics.GenericAPIView):
    serializer_class = OtpSerializer

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email Doesn't Exist!!")
            return redirect('/forgot-pass/')
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND, detail="Email doesn't exist!")
        else:
            no = random.randint(1000, 99999)
            # tempary = Otp.objects.post(otp=no)
            gmail_user = 'pankajspsq@gmail.com'
            gmail_password = 'Pankaj@05'

            sent_from = gmail_user
            to = email
            subject = 'Welcome to Wayrem'
            body = f'Your One time password is {no}'

            email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sent_from, ", ".join(to), subject, body)

            try:
                smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                smtp_server.ehlo()
                smtp_server.login(gmail_user, gmail_password)
                smtp_server.sendmail(sent_from, to, email_text)
                smtp_server.close()
                print("Email sent successfully!")
            except Exception as ex:
                print("Something went wrong….", ex)
            data1 = {"email": request.POST['email'], "otp": no}
            print(data1)
            user = Otp(email=email, otp=no)
            user.save()
            # serializer = self.get_serializer(data=data1)
            # serializer.is_valid(raise_exception=True)
            # print(serializer)
            # user = serializer.save()
            return render(request, 'reset-password.html', {'email': email})
            # return redirect('/reset-pass/')
            # print(request)
            # user = generate_passcode(request)
            # return Response({
            #     "user": OtpSerializer(user, context=self.get_serializer_context()).data,
            # })


def forgot_pass(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, 'User doesnot exist!!')
            return redirect('/forgot-pass/')
        else:
            no = random.randint(1000, 99999)
            # tempary = Otp.objects.post(otp=no)
            temporary = Otp(email=email, otp=no)
            temporary.save()
            gmail_user = 'shubhamrai028@gmail.com'
            gmail_password = 'shubham@nodejs'

            sent_from = gmail_user
            to = ['pankajspsq@gmail.com']
            subject = 'Welcome to Wayrem'
            body = f'Your One time password is {no}'

            email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sent_from, ", ".join(to), subject, body)

            try:
                smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                smtp_server.ehlo()
                smtp_server.login(gmail_user, gmail_password)
                smtp_server.sendmail(sent_from, to, email_text)
                smtp_server.close()
                print("Email sent successfully!")
            except Exception as ex:
                print("Something went wrong….", ex)

            # send_otp(email)
            # common_msg = schema_common.ResponseCommonMessage(
            # status=status.HTTP_200_OK, message=constants.HTTP_RESPONSE_SUCCESS)
        context = {"status": "200", "message": "Success", "email": email}
        return render(request, 'reset-password.html', context)
    return render(request, 'forgot-password.html')
# Sub-Admin Registration


# try


class LogoutView(APIView):
    def get(self, request):

        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        logout(request)
        return redirect('/')


class UsersList(APIView):
    template_name = "userlist.html"

    def get(self, request, format=None):
        userlist = CustomUser.objects.all()
        return render(request, self.template_name, {"userlist": userlist})


# Accounts Code

# ! API's Created Here

# Custom Register View


# Role API View
class RoleAPI(generics.GenericAPIView):
    serializer_class = RoleSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": RoleSerializer(user, context=self.get_serializer_context()).data,
        })


def reset_password(request):
    return render(request, 'reset-password.html', )


class Reset_Password(generics.GenericAPIView):
    serializer_class = ResetSerializer

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        print(email)
        otp = request.POST.get('otp')
        newpassword = request.POST.get('newpassword')
        print(newpassword)
        user = Otp.objects.filter(email=email, otp=otp).first()

        if user:
            new_user = CustomUser.objects.get(email=email)
            new_user.password = make_password(newpassword)
            new_user.save()
            return redirect('/')
        else:
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND, detail="Something doesn't exist!")
            return render(request, 'page-404.html')


class ResetPassword(APIView):
    def get(self, request, format=None):
        return render(request, 'resetpwd.html')

    def post(self, request):
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User does not Exist!!")
            return redirect('/resetpassword/')
        if not check_password(old_password, user.password):
            messages.error(request, "Old Password not match !!")
            return redirect('/resetpassword/')
        user.password = make_password(new_password)
        user.save()
        return redirect('/dashboard/')
