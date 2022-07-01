from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField, CharField
from django import forms
from django.forms import widgets
from wayrem_admin.models import Orders, OrderTransactions, StatusMaster
from django.forms import ModelForm
from wayrem_admin.utils.constants import *
from wayrem_admin.models import BusinessType

from django.forms import Select

class Select(Select):
    def create_option(self, *args,**kwargs):
        option = super().create_option(*args,**kwargs)
        if not option.get('value'):
            option['attrs']['disabled'] = 'disabled'

        if option.get('value') == 17:
            option['attrs']['disabled'] = 'disabled'
        
        return option

class OrderUpdatedPaymentStatusForm(ModelForm):
    payment_status = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in StatusMaster.objects.filter(status_type=PAYMENT_STATUS, status=1)]
        self.fields['payment_status'].choices = order_choices

    class Meta:
        model = OrderTransactions
        fields = ['payment_status']


class OrderStatusUpdatedForm(ModelForm):
    status = forms.ChoiceField(required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_id = kwargs['instance']
        
        order_status_id = Orders.objects.filter(ref_number=order_id).first()
        order_id=order_status_id.id
        order_transaction=OrderTransactions.objects.filter(order_id=order_id).first()
        if (order_transaction.payment_mode_id == BANKTRANSFER_MODE) and (order_transaction.payment_status_id == PAYMENT_STATUS_PENDING or order_transaction.payment_status_id == PAYMENT_STATUS_DECLINED or order_transaction.payment_status_id == PAYMENT_STATUS_REJECTED):
            self.fields['status'].widget=Select(attrs={'class': 'form-control form-control-select'})
        else:
            self.fields['status'].widget=forms.Select(attrs={'class': 'form-control form-control-select'})
        if order_status_id.status.id == ORDER_PENDING_APPROVED:
            exclude_status = [OREDER_PENDING_RECURENCE]
        elif order_status_id.status.id == OREDER_PENDING_RECURENCE:
            exclude_status = [ORDER_PENDING_APPROVED]
        else:
            exclude_status = [OREDER_PENDING_RECURENCE, ORDER_PENDING_APPROVED]

        order_choices = [(get_users_options.pk, get_users_options.description)
                         for get_users_options in StatusMaster.objects.filter(status_type=ORDER_STATUS, status=1).exclude(id__in=exclude_status)]
        self.fields['status'].choices = order_choices

    class Meta:
        model = Orders
        fields = ['status']
        

class OrderAdvanceFilterForm(ModelForm):
    status = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))
    order_ref = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    orderrefer = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    contact = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    customer_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    start_date = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    end_date = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)

    #choice_status = (("1", "All"), ("2", "Home business"),("3", "None home business"))
    choice_status = [(get_users_options.pk, get_users_options.business_type) for get_users_options in BusinessType.objects.filter(status=1)]
    choice_status.insert(0, ('0', 'All'))

    business_type = forms.ChoiceField(choices=choice_status, widget=forms.Select(attrs={'class': 'form-select', }),required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in StatusMaster.objects.filter(status_type=ORDER_STATUS, status=1)]
        order_choices.insert(0, ('', 'Select Status'))
        self.fields['status'].choices = order_choices

    class Meta:
        model = Orders
        fields = ['orderrefer', 'order_ref', 'status', 'contact',
                  'customer_name', 'start_date', 'end_date', 'business_type']


class OrderStatusFilter(ModelForm):
    status = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in StatusMaster.objects.filter(status_type=ORDER_STATUS, status=1)]
        order_choices.insert(0, ('', 'All order status'))
        self.fields['status'].choices = order_choices

    class Meta:
        model = Orders
        fields = ['status']


class OrderStatusDetailForm(ModelForm):
    #status = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'form-control form-control-select'}))
    status = forms.ChoiceField(required=True)

    def __init__(self, status_id,order_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        order_transaction=OrderTransactions.objects.filter(order_id=order_id).first()
        if (order_transaction.payment_mode_id == BANKTRANSFER_MODE) and (order_transaction.payment_status_id == PAYMENT_STATUS_PENDING or order_transaction.payment_status_id == PAYMENT_STATUS_DECLINED or order_transaction.payment_status_id == PAYMENT_STATUS_REJECTED):
            self.fields['status'].widget=Select(attrs={'class': 'form-control form-control-select'})
        else:
            self.fields['status'].widget=forms.Select(attrs={'class': 'form-control form-control-select'})
        if status_id == ORDER_PENDING_APPROVED:
            exclude_status = [OREDER_PENDING_RECURENCE]
        elif status_id == OREDER_PENDING_RECURENCE:
            exclude_status = [ORDER_PENDING_APPROVED]
        else:
            exclude_status = [OREDER_PENDING_RECURENCE, ORDER_PENDING_APPROVED]

        order_choices = [(get_users_options.pk, get_users_options.description)
                         for get_users_options in StatusMaster.objects.filter(status_type=ORDER_STATUS, status=1).exclude(id__in=exclude_status)]
        self.fields['status'].choices = order_choices

    class Meta:
        model = Orders
        fields = ['status']
