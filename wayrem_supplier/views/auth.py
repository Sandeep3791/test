from django.contrib.messages.api import success
from wayrem_supplier.models import PurchaseOrder, Supplier, OtpDetails, Notification, PO_log, Invoice
from django.contrib import messages
from django.shortcuts import render, redirect
from wayrem_supplier.forms import ProfileUpdateForm
import random
import smtplib
import uuid
from datetime import *
from django.views.generic import RedirectView
from django.urls import reverse
from wayrem_supplier.models.StaticModels import EmailTemplateModel
from wayrem_supplier.services import send_email
from wayrem_supplier.views import purchase_order
from rest_framework.decorators import api_view
from wayrem_supplier.create_prefix_models import create_supplier_models_cluster, runtime_migrations
from django.http import JsonResponse


def login(request):
    if request.method == 'POST':
        user = Supplier.objects.filter(email=request.POST.get('email')).first()
        print(user)
        if not user:
            messages.error(request, "User doesn't exist!")
            return redirect('wayrem_supplier:login')
        if user.password == request.POST.get('password'):
            request.session['supplier'] = user.username
            request.session['supplier_id'] = user.id
            return redirect('wayrem_supplier:supplier_profile')
        else:
            messages.error(request, "incorrect credential.Please try again")
            return redirect('wayrem_supplier:login')
    else:
        if request.session.get('supplier'):
            return redirect('wayrem_supplier:root')
        else:
            return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'GET':
        request.session.flush()
        return redirect('wayrem_supplier:login')


def supplier_profile(request):
    if request.session.get('supplier'):
        user = Supplier.objects.get(username=request.session.get('supplier'))
        supplier_id = request.session.get("supplier_id")
        po_status = PurchaseOrder.objects.filter(
            supplier_name=supplier_id).values('status')
        waiting_po = po_status.filter(status='waiting for approval').values(
            'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
        approved_po = po_status.filter(status='approved').values(
            'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
        active_po = waiting_po + approved_po
        complete_po = po_status.filter(status='delivered').values(
            'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
        po_delivered_price = PurchaseOrder.objects.filter(
            supplier_name=supplier_id, status='delivered')
        total_sales = sum([float(po_price.supplier_product.price)
                          for po_price in po_delivered_price])
        return render(request, 'dashboard.html', {'user': user, 'active_po': active_po, 'complete_po': complete_po, 'total_sales': total_sales})
    else:
        return redirect('wayrem_supplier:root')


def update_supplier_profile(request):
    if request.session.get('supplier') is None:
        return redirect('wayrem_supplier:login')
    obj = request.session.get('supplier')
    user = Supplier.objects.filter(username=obj).first()

    context = {}
    form = ProfileUpdateForm(request.POST or None,
                             request.FILES or None, instance=user)
    context = {'form': form, 'username': user.username,
               'email': user.email, 'logo': user.logo}
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data['email']
            contact = form.cleaned_data['contact']
            address = form.cleaned_data['address']
            logo = form.cleaned_data['logo']
            company_name = form.cleaned_data['company_name']
            delivery_incharge = form.cleaned_data['delivery_incharge']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            company_phone_no = form.cleaned_data['company_phone_no']
            company_email = form.cleaned_data['company_email']
            registration_no = form.cleaned_data['registration_no']
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
            contact_person_name = form.cleaned_data['contact_person_name']
            contact_phone_no = form.cleaned_data['contact_phone_no']

            supplier_record = Supplier.objects.filter(id=user.id).first()
            supplier_record.email = email
            supplier_record.contact = contact
            supplier_record.address = address
            supplier_record.logo = logo
            supplier_record.company_name = company_name
            supplier_record.delivery_incharge = delivery_incharge
            supplier_record.first_name = first_name
            supplier_record.last_name = last_name
            supplier_record.company_phone_no = company_phone_no
            supplier_record.company_email = company_email
            supplier_record.registration_no = registration_no
            supplier_record.from_time = from_time
            supplier_record.to_time = to_time
            supplier_record.contact_person_name = contact_person_name
            supplier_record.contact_phone_no = contact_phone_no
            supplier_record.save()
        return redirect('wayrem_supplier:supplier_profile')

    return render(request, 'update_supplier_profile.html', context)


# forgot password
def forgot_password(request):
    if request.method == 'GET':
        return render(request, 'forgot-password.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        user = Supplier.objects.filter(email=email).first()
        print(user)
        if not user:
            messages.error(request, "Email Doesn't Exist!!")
            return redirect('wayrem_supplier:forgot-pass')
        else:
            no = random.randint(1000, 99999)
            to = email
            email_template = EmailTemplateModel.objects.get(key="otp_supplier")
            subject = email_template.subject
            body = email_template.message_format.format(
                supplier=user.username, otp=no)
            send_email(to, subject, body)

            data1 = {"email": request.POST['email'], "otp": no}
            print(data1)
            user = OtpDetails(email=email, otp=no, created_at=datetime.now())
            user.save()
            return render(request, 'reset-password.html', {'email': email})


def reset_password(request):

    if request.method == 'GET':
        return render(request, 'reset-password.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        SpecialSym = ['$', '@', '#', '%', '&', '!', '~']
        message = f"Password must contain at least 8 characters including 1-uppercase letter, 1-lowercase letter, number and 1-special character '{SpecialSym}' "

        if len(new_password) < 8:
            messages.error(request, message)
            return redirect('wayrem_supplier:reset-pass')

        elif not any(char.isdigit() for char in new_password):
            messages.error(request, message)
            return redirect('wayrem_supplier:reset-pass')

        elif not any(char.isupper() for char in new_password):
            messages.error(request, message)
            return redirect('wayrem_supplier:reset-pass')

        elif not any(char.islower() for char in new_password):
            messages.error(request, message)
            return redirect('wayrem_supplier:reset-pass')

        elif not any(char in SpecialSym for char in new_password):
            messages.error(request, message)
            return redirect('wayrem_supplier:reset-pass')

        elif new_password != confirm_password:
            messages.error(request, "Password Doesn't Match!")
            return redirect('wayrem_supplier:reset-pass')

        user = OtpDetails.objects.filter(email=email, otp=otp).first()
        if user:
            new_user = Supplier.objects.get(email=email)
            new_user.password = new_password
            new_user.save()
            user.delete()
            return redirect('wayrem_supplier:login')
        else:
            messages.error(request, "Invalid OTP!")
            return render(request, 'reset-password.html')


class RootUrlView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.session.get('supplier_id'):
            return reverse('wayrem_supplier:login')
        return reverse('wayrem_supplier:supplier_profile')


def notifications_seen(request, id=None):
    notify = Notification.objects.filter(id=id).first()
    a = notify.message
    po_no = list(filter(lambda word: word[0:3] == 'PO/', a.split()))[0]
    po = PurchaseOrder.objects.filter(po_name=po_no).first()
    po_id = po.po_id
    notify.delete()
    return redirect('wayrem_supplier:podetails', po_id)


def notifications_clear(request):
    notify = Notification.objects.filter(
        supplier_id=request.session['supplier_id'])
    notify.delete()
    return redirect('wayrem_supplier:root')


@api_view(['POST'])
def SupplierAddApi(request):
    if request.method == 'POST':
        payload = request.data
        username = payload['username']
        create_supplier_models_cluster(username)
    return JsonResponse({"status": True, "message": "model create successfully"})


@api_view(['GET'])
def SupplierAddMigrationsApi(request):
    runtime_migrations()
    return JsonResponse({"status": True, "message": "model migrated successfully"})
