from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField,CharField
from django import forms
from django.forms import widgets
from wayrem_admin.models_orders import Orders, OrderStatus
from django.forms import ModelForm


class OrderStatusUpdatedForm(ModelForm):
    status = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in OrderStatus.objects.filter()]
        self.fields['status'].choices = order_choices
        #self.fields['status'].queryset = OrderStatus.objects

    class Meta:
        model = Orders
        fields = ['status']

class OrderAdvanceFilterForm(ModelForm):
    status = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-control form-control-select'}))
    order_ref = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    orderrefer=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    contact=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    customer_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)

    start_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    end_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in OrderStatus.objects.filter()]
        order_choices.insert(0,('','Select Status'))
        self.fields['status'].choices = order_choices
    class Meta:
        model = Orders
        fields = ['orderrefer','order_ref','status','contact','customer_name','start_date','end_date']
       
class OrderStatusDetailForm(ModelForm):
    status = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        order_choices = [(get_users_options.pk, get_users_options.name)
                         for get_users_options in OrderStatus.objects.filter()]
        self.fields['status'].choices = order_choices
    class Meta:
        model = Orders
        fields = ['status']