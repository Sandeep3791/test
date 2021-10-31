from sqlalchemy import create_engine
from pyvirtualdisplay import Display
from wayrem.settings import BASE_DIR
import pandas as pd
from django.template.loader import get_template
import pdfkit
import requests
from .forms import *
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
import smtplib
from django.contrib.auth import authenticate, login, logout
from django.views import View
from wayrem_admin.models import *
import random
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import uuid
from django.http import HttpResponse
from wayrem_admin.decorators import role_required
import json
from django.db import connection
# Create your views here.


@login_required(login_url='/')
def dashboard(request):
    subadmins = CustomUser.objects.exclude(is_superuser=True)
    suppliers = SupplierRegister.objects.all()
    products = Products.objects.all()
    context = {
        'subadmins': len(subadmins),
        'suppliers': len(suppliers),
        'products': len(products)
    }

    return render(request, 'dashboard.html', context)


def anonymous(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


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
        # print(username)
        # print(password)

        user = CustomUser.objects.filter(username=username).first(
        )
        if user is None:
            # raise AuthenticationFailed("User Not Found!")
            # return JsonResponse({"error": "User Not Found!"})
            messages.error(request, "User not found!")
            return redirect('/')
        if not check_password(password, user.password):
            messages.error(request, "Incorrect Password!")
            return redirect('/')
            # raise AuthenticationFailed("incorrect Password!")

        if not user.is_active:
            messages.error(request, "User is Blocked!")
            return redirect('/')
            # return JsonResponse({"error": "User is Blocked"})

        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, "Logged in Successfully!")
        return redirect('/dashboard/')


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
                role_obj = Roles.objects.get(id=role)
                password = form.cleaned_data['password1']
                user = CustomUser.objects.create_user(
                    username=username, email=email, contact=contact, role=role_obj, password=password)
                user.save()
                # form.save()
                gmail_user = 'pankajspsq@gmail.com'
                gmail_password = 'Pankaj@05'

                sent_from = gmail_user
                to = email
                subject = 'Welcome to Wayrem'
                body = f'Your credential for wayrem are:\n username: {username} \n Email_id: {email} \n Password: {password} \n '
                # Role: {role}
                email_text = f"From:{sent_from},To:{to} Subject: {subject}  {body}"
                try:
                    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    smtp_server.ehlo()
                    smtp_server.login(gmail_user, gmail_password)
                    smtp_server.sendmail(sent_from, to, email_text)
                    smtp_server.close()
                    print("Email sent successfully!")
                except Exception as ex:
                    print("Something went wrong….", ex)
                messages.success(request, 'User Created Successfully!!')
                return redirect('/dashboard/')
        else:
            form = SubAdminForm()
        return render(request, 'accounts/register.html', {"form": form})
    else:
        return redirect('/dashboard/')


class Forgot_Password(View):
    # serializer_class = OtpSerializer

    @method_decorator(anonymous(login_url='/dashboard/'))
    def get(self, request):
        return render(request, 'forgot-password.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email Doesn't Exist!")
            return redirect('/forgot-password/')
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
            # return redirect('/reset-password/')
            # print(request)
            # user = generate_passcode(request)
            # return Response({
            #     "user": OtpSerializer(user, context=self.get_serializer_context()).data,
            # })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')


class UsersList(View):
    template_name = "userlist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        userlist = CustomUser.objects.all()
        user_role = Roles.objects.all()
        return render(request, self.template_name, {"userlist": userlist, "roles": user_role})


class Reset_Password(View):
    # serializer_class = ResetSerializer

    def get(self, request):
        return render(request, 'reset-password.html', )

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        print(email)
        otp = request.POST.get('otp')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirm_password')
        if newpassword != confirmpassword:
            messages.error(request, "Password Doesn't Match!")
            return redirect('/reset-password/')
        print(newpassword)
        user = Otp.objects.filter(email=email, otp=otp).first()

        if user:
            print("Working")
            new_user = CustomUser.objects.get(email=email)
            new_user.password = make_password(newpassword)
            new_user.save()
            messages.success(request, "Password Changed Successfully!")
            return redirect('/')
        else:
            print("Not Working")
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND, detail="Something doesn't exist!")
            messages.error(request, "OTP Invalid!")
            return redirect('/reset-password/')


class Change_PasswordView(PasswordContextMixin, FormView):
    # form_class = PasswordChangeForm
    form_class = ChangePasswordForm
    success_url = reverse_lazy('dashboard')
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
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed.")
        return super(FormView, self).form_valid(form)


# Delete User
class DeleteUser(View):
    def post(self, request):
        userid = request.POST.get('userid')
        user = CustomUser.objects.get(pk=userid)
        user.delete()
        return redirect('/users-list/')


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
        return redirect('/users-list/')


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
            # kwargs['instance'] = CustomUser.objects.get(email=email, first_name=fname, last_name=lname, contact=contact, gender=gender, dob=dob, address=address, city=city, zip_code=zip_code )
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
            return redirect('/update_profile/')
    user = CustomUser.objects.get(username=request.user.username)
    form = ProfileUpdateForm(instance=user)
    return render(request, 'settings.html', {'form': form})


def supplier_category(request):
    return render(request, 'edit_categories.html')


@login_required(login_url='/')
def create_category(request):
    context = {}
    # user = SupplierProfileModel.objects.filter(user_id = request.user.id).first()
    form = CategoryCreateForm(request.POST or None, request.FILES or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            print('valid')
            form.save()
            return redirect('/categories-list/')
        else:
            print("Invalid")
    return render(request, 'edit_categories.html', context)


class CategoriesList(View):
    template_name = "categorieslist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        categorieslist = Categories.objects.all()
        # user_role = Roles.objects.all()
        # "roles":user_role
        return render(request, self.template_name, {"categorieslist": categorieslist})


class DeleteCategories(View):
    def post(self, request):
        categoriesid = request.POST.get('category_id')
        categories = Categories.objects.get(id=categoriesid)
        categories.delete()
        return redirect('/categories-list/')


@login_required(login_url='/')
def update_categories(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = Categories.objects.get(id=id)
        form = CategoryCreateForm(
            request.POST or None, request.FILES or None, instance=user)
        if form.is_valid():
            print("FORM")
            name = form.cleaned_data['name']
            category_image = form.cleaned_data['category_image']
            description = form.cleaned_data['description']
            user.name = name
            user.category_image = category_image
            user.description = description
            user.save()
            print("Here")
            return redirect('/categories-list/')
    user = Categories.objects.get(id=id)
    form = CategoryCreateForm(instance=user)
    return render(request, 'update_category.html', {'form': form, 'id': user.id})


@login_required(login_url='/')
def supplier_register(request):

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SupplierRegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                category_name = form.cleaned_data['category_name']
                user = SupplierRegister(
                    username=username, email=email, password=password)
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'CREATE TABLE If NOT Exists {username}_product(`product_id` Varchar(250), `supplier_product_id` Varchar(250),`quantity` Integer, `price` Float , `availability` boolean not null default 0 , `status` boolean not null default 0 ,PRIMARY KEY(`product_id`));')
                user.save()
                user.category_name.set(category_name)
                user.save()
                # form.save()
                gmail_user = 'pankajspsq@gmail.com'
                gmail_password = 'Pankaj@05'

                sent_from = gmail_user
                to = email
                subject = 'Welcome to Wayrem'
                body = f'Your credential for wayrem are:\n username: {username} \n Email_id: {email} \n Password: {password} \n '
                # Role: {role}
                email_text = f"From:{sent_from},To:{to} Subject: {subject}  {body}"
                try:
                    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    smtp_server.ehlo()
                    smtp_server.login(gmail_user, gmail_password)
                    smtp_server.sendmail(sent_from, to, email_text)
                    smtp_server.close()
                    print("Email sent successfully!")
                except Exception as ex:
                    print("Something went wrong….", ex)
                messages.success(request, 'User Created Successfully!!')
                return redirect('/dashboard/')
        else:
            form = SupplierRegisterForm()
        return render(request, 'accounts/supplier_register.html', {"form": form})
    else:
        return redirect('/dashboard/')


class SupplierList(View):
    template_name = "supplierlist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        supplierlist = SupplierRegister.objects.all()
        # user_role = Roles.objects.all()
        # "roles":user_role
        return render(request, self.template_name, {"supplierlist": supplierlist})


class DeleteSupplier(View):
    def post(self, request):
        supplierid = request.POST.get('supplier_id')
        user = SupplierRegister.objects.get(pk=supplierid)
        user.delete()
        return redirect('/supplier-list/')


# Active/Block
class Active_BlockSupplier(View):

    @method_decorator(login_required(login_url='/'))
    def get(self, request, id):
        user = SupplierRegister.objects.get(pk=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('/supplier-list/')


# Roles CRUD Start-----------------------------


@role_required('Roles View')
def rolesList(request):
    context = {}
    roles = Roles.objects.all().order_by('-pk')
    context['roles'] = roles
    return render(request, 'roles_crud_pages/rolesList.html', context)


@role_required('Roles Add')
def createRoles(request):
    context = {}
    form = RoleForm(label_suffix='')
    context['form'] = form
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role Added")
            return redirect('roles_list')
    return render(request, 'roles_crud_pages/createRoles.html', context)


@role_required('Roles Edit')
def cupdateRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    form = RoleForm(instance=role, label_suffix='')
    context['form'] = form
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(request, "Role Updated")
            return redirect('roles_list')
    return render(request, 'roles_crud_pages/createRoles.html', context)


@role_required('Roles Delete')
def activeUnactiveRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    if role.status == "Active":
        role.status = 'Inactive'
    else:
        role.status = 'Active'
    role.save()
    messages.success(request, "Role Updated")
    return redirect('roles_list')


def viewRoles(request):
    context = {}
    role = get_object_or_404(Roles, id=request.GET.get('id'))
    form = RoleViewForm(instance=role, label_suffix='')
    context['form'] = form
    context['role_name'] = Roles.objects.get(id=request.GET.get('id'))
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(request, "Role Updated")
            return redirect('roles_list')
    return render(request, 'roles_crud_pages/view_roles.html', context)
# Roles CRUD End---------------------------------------------------------------------


def delSession(request):
    try:
        for key in list(request.session.keys()):
            if not key.startswith("_"):  # skip keys set by the django system
                del request.session[key]
    except:
        pass
    return


def barcodeDetail(code):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'user_key': 'only_for_dev_or_pro',
        'key_type': '3scale'
    }
    resp = requests.get(
        f'https://api.upcitemdb.com/prod/trial/lookup?upc={code}', headers=headers)
    data = json.loads(resp.text)
    return data


def inputBar(request):
    if request.method == "POST":
        delSession(request)
        user_code = request.POST.get('code')
        data = barcodeDetail(user_code)

        try:
            request.session['SKU'] = data['items'][0]['ean']
            request.session['product_name'] = data['items'][0]['title']
            request.session['description'] = data['items'][0]['description']
            request.session['model'] = data['items'][0]['model']
            request.session['weight'] = data['items'][0]['weight']
            request.session['price'] = data['items'][0]['price']
        except:
            pass
        return redirect('/product-view-one/')
    # context = {
    #     'ean': request.session['ean'],
    #     'title': request.session['title'],
    #     'description': request.session['description'],
    #     'model': request.session['model']
    # }
    return render(request, 'inputBar.html')


def product(request):
    delSession(request)
    # messages.success(request, "Lorem ipsum")
    return render(request, 'preproduct.html')


def product_view_one(request):
    # date_of_mfg = datetime.date(json.loads(
    #     request.session.get('date_of_exp')), "%Y-%m-%d")
    # date_of_exp = datetime.strptime(json.loads(
    #     request.session.get('date_of_exp')), "%Y-%m-%d").date(),

    initial = {
        'SKU': request.session.get('SKU', None),
        'product_category': request.session.get('product_category', None),
        'product_code': request.session.get('product_code', None),
        'product_name': request.session.get('product_name', None),
        'feature_product': request.session.get('feature_product', None),
        'product_deliverable': request.session.get('product_deliverable', None),
        'date_of_mfg': request.session.get('date_of_mfg', None),
        'date_of_exp': request.session.get('date_of_exp', None),
        'mfr_name': request.session.get('mfr_name', None),
        'supplier_name': request.session.get('supplier_name', None),
    }
    context = {}
    form = ProductFormOne(request.POST, initial=initial)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            request.session['SKU'] = form.cleaned_data['SKU']
            request.session['product_category'] = form.cleaned_data['product_category']
            request.session['product_code'] = form.cleaned_data['product_code']
            request.session['product_name'] = form.cleaned_data['product_name']
            request.session['feature_product'] = form.cleaned_data['feature_product']
            request.session['product_deliverable'] = form.cleaned_data['product_deliverable']
            request.session['date_of_mfg'] = str(
                form.cleaned_data['date_of_mfg'])
            request.session['date_of_exp'] = str(
                form.cleaned_data['date_of_exp'])
            # json.dumps(doe, indent=4, sort_keys=True, default=str)
            request.session['mfr_name'] = form.cleaned_data['mfr_name']
            request.session['supplier_name'] = form.cleaned_data['supplier_name']

            # return HttpResponseRedirect(reverse('product-view-two'))
            return redirect('/product-view-two/')
            # return HttpResponse(render(request,'path_to_your_view.html'))
    else:
        context['form'] = ProductFormOne(initial=initial)
    return render(request, 'product1.html', context)

# # ----------------------------------------------------------------------------


@ login_required(login_url='/')
def product_view_two(request):
    initial = {
        'product_weight': request.session.get('product_weight', None),
        'unit': request.session.get('unit', None),
        'price': request.session.get('price', None),
        'discount': request.session.get('discount', None),
        'dis_abs_percent': request.session.get('dis_abs_percent', None),
        'wayrem_margin': request.session.get('wayrem_margin', None),
        'wayrem_abs_percent': request.session.get('wayrem_abs_percent', None),
        'package_count': request.session.get('package_count', None),
        'product_meta_key': request.session.get('product_meta_key', None),
    }

    context = {}
    form = ProductFormTwo(request.POST, initial=initial)
    context['form'] = form
    # form = ProductFormTwo(request.POST or None, initial=initial)
    if request.method == 'POST':
        print("post")
        if form.is_valid():
            print("valid")
            request.session['product_weight'] = float(
                form.cleaned_data['product_weight'])
            request.session['unit'] = form.cleaned_data['unit']
            price = form.cleaned_data['price']
            request.session['price'] = float(price)
            request.session['discount'] = float(form.cleaned_data['discount'])
            request.session['dis_abs_percent'] = form.cleaned_data['dis_abs_percent']
            request.session['wayrem_margin'] = form.cleaned_data['wayrem_margin']
            request.session['wayrem_abs_percent'] = form.cleaned_data['wayrem_abs_percent']
            request.session['package_count'] = float(
                form.cleaned_data['package_count'])
            request.session['product_meta_key'] = form.cleaned_data['product_meta_key']
            return redirect('/product-view-three/')
    else:
        context['form'] = ProductFormTwo(initial=initial)
    return render(request, 'product2.html', context)

# ----------------------------------------------------------------------------------
# @login_required(login_url='/')


def product_view_three(request):
    initial = {
        # 'product_name': request.session.get('product_name', None),
        'description': request.session.get('description', None),
        'calories1': request.session.get('calories1', None),
        'calories2': request.session.get('calories2', None),
        'calories3': request.session.get('calories3', None),
        'calories4': request.session.get('calories4', None),
        'ingredients1': request.session.get('ingredients1', None),
        'ingredients2': request.session.get('ingredients2', None),
        'ingredients3': request.session.get('ingredients3', None),
        'ingredients4': request.session.get('ingredients4', None),
        'product_qty':  request.session.get('product_qty', None),
    }
    context = {}
    form = ProductFormThree(request.POST, initial=initial)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            request.session['description'] = form.cleaned_data['description']
            calories1 = form.cleaned_data['calories1']
            calories2 = form.cleaned_data['calories2']
            calories3 = form.cleaned_data['calories3']
            calories4 = form.cleaned_data['calories4']
            request.session['calories1'] = float(calories1)
            request.session['calories2'] = float(calories2)
            # request.session['calories2'] = json.dumps(
            # calories2, cls=DecimalEncoder)
            request.session['calories3'] = float(calories3)
            request.session['calories4'] = float(calories4)
            request.session['ingredients1'] = form.cleaned_data['ingredients1']
            request.session['ingredients2'] = form.cleaned_data['ingredients2']
            request.session['ingredients3'] = form.cleaned_data['ingredients3']
            request.session['ingredients4'] = form.cleaned_data['ingredients4']
            request.session['product_qty'] = form.cleaned_data['product_qty']
            # return HttpResponseRedirect(reverse('product_view_two'))
            return redirect('/product-view-four/')
    else:
        context['form'] = ProductFormThree(initial=initial)
    return render(request, 'product3.html', context)

# # -------------------------------------------------------------------------------


def inst_Supplier(value):
    return SupplierRegister.objects.get(id=value)


def inst_Category(value):
    return Categories.objects.get(id=value)


def inst_Ingridient(value):
    return Ingredients.objects.get(id=value)


def inst_Product(value):
    return Products.objects.get(id=value)


def product_view_four(request):
    # initial = {
    #     'wayrem_margin': request.session.get('wayrem_margin', None),
    #     'wayrem_abs_percent': request.session.get('wayrem_abs_percent', None),
    # }
    context = {}
    form = ProductFormFour(request.POST, request.FILES)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            sku = request.session['SKU']
            product_code = request.session['product_code']
            product_meta_key = request.session['product_meta_key']
            feature_product = request.session['feature_product']
            product_deliverable = request.session['product_deliverable']
            mfr_name = request.session['mfr_name']
            date_of_mfg = request.session['date_of_mfg']
            date_of_exp = request.session['date_of_exp']
            product_name = request.session['product_name']
            description = request.session['description']
            calories1 = request.session['calories1']
            calories2 = request.session['calories2']
            calories3 = request.session['calories3']
            calories4 = request.session['calories4']
            product_qty = request.session['product_qty']
            product_weight = request.session['product_weight']
            unit = request.session['unit']
            price = request.session['price']
            discount = request.session['discount']
            wayrem_margin = request.session['wayrem_margin']
            wayrem_abs_percent = request.session['wayrem_abs_percent']
            package_count = request.session['package_count']
            ingredients1 = inst_Ingridient(request.session['ingredients1'])
            ingredients2 = inst_Ingridient(request.session['ingredients2'])
            ingredients3 = inst_Ingridient(request.session['ingredients3'])
            ingredients4 = inst_Ingridient(request.session['ingredients4'])
            category = [inst_Category(i)
                        for i in request.session['product_category']]
            supplier = [inst_Supplier(i)
                        for i in request.session['supplier_name']]
            # c
            image1 = form.cleaned_data['image1']
            image2 = form.cleaned_data['image2']
            image3 = form.cleaned_data['image3']
            image4 = form.cleaned_data['image4']
            image5 = form.cleaned_data['image5']

            prod = Products(SKU=sku, product_code=product_code, product_meta_key=product_meta_key, feature_product=feature_product, product_deliverable=product_deliverable, date_of_mfg=date_of_mfg, date_of_exp=date_of_exp,
                            mfr_name=mfr_name, product_name=product_name, description=description,
                            calories1=calories1, calories2=calories2, calories3=calories3, calories4=calories4, ingredients1=ingredients1,
                            ingredients2=ingredients2, ingredients3=ingredients3, ingredients4=ingredients4, product_qty=product_qty, product_weight=product_weight,
                            unit=unit, price=price, discount=discount, package_count=package_count, wayrem_margin=wayrem_margin, image1=image1, image2=image2, image3=image3, image4=image4, image5=image5, wayrem_abs_percent=wayrem_abs_percent)
            prod.save()
            prod.product_category.set(category)
            prod.supplier_name.set(supplier)
            prod.save()
            try:
                del request.session['ean']
                del request.session['title']
                del request.session['description']
                del request.session['model']
            except:
                pass
            return redirect('/dashboard/')
    else:
        context['form'] = ProductFormFour()
    return render(request, 'product4.html', context)


class ProductList(View):
    template_name = "productlist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        productslist = Products.objects.all()
        # user_role = Roles.objects.all()
        # "roles":user_role
        return render(request, self.template_name, {"productslist": productslist})


@login_required(login_url='/')
def create_ingredients(request):
    context = {}
    # user = SupplierProfileModel.objects.filter(user_id = request.user.id).first()
    form = IngredientsCreateForm(request.POST or None)
    context['form'] = form
    if request.method == "POST":
        print("POST")
        if form.is_valid():
            print('valid')
            form.save()
            return redirect('/ingredients-list/')
        else:
            print("Invalid")
    return render(request, 'create_ingredients.html', context)


class IngredientsList(View):
    template_name = "ingredientslist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        ingredientslist = Ingredients.objects.all()
        # user_role = Roles.objects.all()
        # "roles":user_role
        return render(request, self.template_name, {"ingredientslist": ingredientslist})


class DeleteIngredients(View):
    def post(self, request):
        ingredientsid = request.POST.get('ingredients_id')
        ingredients = Ingredients.objects.get(id=ingredientsid)
        ingredients.delete()
        return redirect('/ingredients-list/')


@login_required(login_url='/')
def update_ingredients(request, id=None, *args, **kwargs):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = Ingredients.objects.get(id=id)
        form = IngredientsCreateForm(
            request.POST or None, instance=user)
        if form.is_valid():
            print("FORM")
            ingredients_name = form.cleaned_data['ingredients_name']
            ingredients_status = form.cleaned_data['ingredients_status']
            user.ingredients_name = ingredients_name
            user.ingredients_status = ingredients_status
            user.save()
            print("Here")
            return redirect('/ingredients-list/')
    user = Ingredients.objects.get(id=id)
    form = IngredientsCreateForm(instance=user)
    return render(request, 'update_ingredients.html', {'form': form, 'id': user.id})


# @login_required(login_url='/')
# def create_purchase_order_PO(request):
#     context = {}
#     # user = SupplierProfileModel.objects.filter(user_id = request.user.id).first()
#     form = PurchaseOrderCreateForm(request.POST or None)
#     context['form'] = form
#     if request.method == "POST":
#         print("POST")
#         if form.is_valid():
#             print('valid')
#             form.save()
#             return redirect('/ingredients-list/')
#         else:
#             print("Invalid")
#     return render(request, 'create_ingredients.html', context)

def create_po1(request):
    return render(request, 'po_step1.html/')


# def create_po2(request):
#     return render(request, 'po_step2.html/')


# Ajax
def load_supplier(request):
    # category = request.GET.get('category_product')
    x = dict(request.GET)
    category = x.get('category_product[]')

    supplier = [SupplierRegister.objects.filter(
        category_name=i).all() for i in category]
    # supplier = SupplierRegister.objects.filter(category_name=category).all()
    return render(request, 'supplier_dropdown.html', {'supplier': supplier})


def pdf_userlist(request):
    query = 'SELECT username, first_name, last_name, is_active, date_joined, email, contact,  dob, gender, address, city, zip_code FROM custom_user'
    df = pd.read_sql_query(
        query, connection)
    df.to_html(
        f'{BASE_DIR}/wayrem_admin/templates/pdf_user.html')
    template = get_template('pdf_user.html')
    html = template.render({'persons': query})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    display = Display(visible=0, size=(1024, 768))
    try:
        display.start()
        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "users.pdf"'
    finally:
        display.stop()
    return response


def pdf_supplier(request):
    query = 'SELECT username, email, contact, address, delivery_incharge, company_name, is_active FROM supplier_master'
    df = pd.read_sql_query(
        query, connection)
    df.to_html(
        f'{BASE_DIR}/wayrem_admin/templates/pdf_supplier.html')
    template = get_template('pdf_supplier.html')
    html = template.render({'persons': query})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    display = Display(visible=0, size=(1024, 768))
    try:
        display.start()
        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "supplier.pdf"'
    finally:
        display.stop()
    return response


def pdf_product(request):
    query = 'SELECT  SKU, product_code, product_meta_key, feature_product, product_deliverable, date_of_mfg, date_of_exp, mfr_name, dis_abs_percent, image1, image2, image3, image4, image5, product_name, description, ingredients1_id, ingredients2_id, ingredients3_id, ingredients4_id, calories1, calories2, calories3, calories4, nutrition, product_qty, product_weight, unit, price, discount, package_count, wayrem_margin, wayrem_abs_percent FROM product_master'
    df = pd.read_sql_query(
        query, connection)
    df.to_html(
        f'{BASE_DIR}/wayrem_admin/templates/pdf_product.html')
    template = get_template('pdf_product.html')
    html = template.render({'persons': query})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    display = Display(visible=0, size=(1024, 768))
    try:
        display.start()
        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "products.pdf"'
    finally:
        display.stop()
    return response


def pdf_category(request):
    query = 'SELECT id, name, category_image, description, created_at, updated_at FROM categories'
    df = pd.read_sql_query(
        query, connection)
    df.to_html(
        f'{BASE_DIR}/wayrem_admin/templates/pdf_category.html')
    template = get_template('pdf_category.html')
    html = template.render({'persons': query})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    display = Display(visible=0, size=(1024, 768))
    try:
        display.start()
        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "categories.pdf"'
    finally:
        display.stop()
    return response


def update_product(request, id=None, *args, **kwargs):
    # print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        prod = Products.objects.get(id=id)
        form = ProductUpdateForm(request.POST or None,
                                 request.FILES or None, instance=prod)
        if form.is_valid():
            print("FORM")

            form.save()
            return redirect('/product-list/')
    prod = Products.objects.get(id=id)
    form = ProductUpdateForm(instance=prod)
    return render(request, 'UpdateProduct.html', {'form': form, 'id': prod.id})


class DeleteProduct(View):
    def post(self, request):
        productid = request.POST.get('product_id')
        products = Products.objects.get(id=productid)
        products.delete()
        return redirect('/product-list/')


def create_purchase_order(request):

    if request.method == "POST":
        form = POForm(request.POST or None, request.FILES or None)
        if 'addMore' in request.POST:
            product_id = request.POST['product_name']
            product_qty = request.POST['product_qty']
            name = inst_Product(product_id)
            x = (product_id, name.product_name, product_qty)
            request.session['products'].append(x)
            po = request.session['products']
            request.session.modified = True
            print('add more')
            return render(request, "po_step1.html", {'form': form, 'po': po})
        elif 'send' in request.POST:
            if request.POST['supplier_name'] == '':
                messages.error(request, "Please Select Supplier!")
                return render(request, "po_step1.html", {'form': form, 'po': request.session['products']})
            else:
                print("supplier")
                supplier_name = inst_Supplier(request.POST['supplier_name'])
                random_no = random.randint(1000, 99999)
                po_id = uuid.uuid4()
                po_name = "PO"+str(random_no)
                for data in request.session['products']:
                    print(data)
                    product_instance = inst_Product(data[0])
                    product_qty = data[2]
                    product_order = PurchaseOrder(
                        po_id=po_id, po_name=po_name, product_name=product_instance, product_qty=product_qty, supplier_name=supplier_name)
                    product_order.save()
                messages.success(
                    request, f"Purchase Order Sent to {supplier_name.username}")
                return redirect('/dashboard/')
        else:
            print("Invalid")
    else:
        form = POForm()
    request.session['products'] = []
    return render(request, "po_step1.html", {'form': form})


class POList(View):
    template_name = "po_list.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        polist = PurchaseOrder.objects.values(
            'po_id', 'po_name', 'supplier_name').distinct()
        pol = []
        for i in polist:
            obj = SupplierRegister.objects.filter(
                id=i['supplier_name']).first()
            pol.append(obj.username)
        mylist = zip(polist, pol)
        # polist = PurchaseOrder.objects.values_list('po_id').distinct()
        # polist = PurchaseOrder.objects.distinct('po_id')
        return render(request, self.template_name, {"userlist": mylist})


def import_ingredients(request):
    if request.method == "POST":
        file = request.FILES["myFileInput"]
        engine = create_engine(
            "mysql+pymysql://root:root1234@localhost/wayrem_9.0?charset=utf8")
        # df = pd.read_excel('files/ingredients.xlsx')
        df = pd.read_excel(file)
        # df.columns = df.iloc[0]
        # df = df.drop(0)
        df = df[df.columns.dropna()]
        df = df.fillna(0)
        ids = []
        uuids = []

        for id_counter in range(0, len(df.index)):
            ids.append(str(uuid.uuid4()))
            df['ingredients_status'] = 'Active'
        for i in ids:
            uuids.append((uuid.UUID(i)).hex)
        df['id'] = uuids

        df.to_sql('ingredients', engine, if_exists='append', index=False)
        return redirect('/ingredients-list/')
    return redirect('/ingredients-list/')


def update_user(request, id=None):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        user = CustomUser.objects.get(id=id)
        form = SubAdminForm(request.POST or None, instance=user)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            contact = form.cleaned_data['contact']
            role = form.cleaned_data['role']
            role_obj = Roles.objects.get(id=role)
            password = form.cleaned_data['password1']
            print("FORM")
            user.username = username
            user.email = email
            user.contact = contact
            user.role_obj = role_obj
            user.password = password
            user.save()
            print("Here")
            return redirect('/users-list/')
    user = CustomUser.objects.get(id=id)
    form = SubAdminForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'id': user.id})


def update_supplier(request, id=None):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        suppl = SupplierRegister.objects.get(id=id)
        form = SupplierRegisterForm(request.POST or None, instance=suppl)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            category_name = form.cleaned_data['category_name']
            print("FORM")
            suppl.username = username
            suppl.email = email
            suppl.password = password
            suppl.category_name.set(category_name)
            suppl.save()
            return redirect('/supplier-list/')
    suppl = SupplierRegister.objects.get(id=id)
    form = SupplierRegisterForm(instance=suppl)
    return render(request, 'update_supplier.html', {'form': form, 'id': suppl.id})


class DeletePO(View):
    def post(self, request):
        po_id = request.POST.get('po_id')
        po_obj = PurchaseOrder.objects.filter(po_id=po_id).all()
        po_obj.delete()
        return redirect('/po-list/')


def viewpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    return render(request, 'view_po.html', {"po": po})


def editpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        count = 1
        for item in po:
            item.po_name = request.POST.get('poname')
            item.product_qty = request.POST.get(f'prodqty{count}')
            item.save()
            count += 1
        return redirect('/po-list/')
    return render(request, 'edit_po.html', {"po": po})
