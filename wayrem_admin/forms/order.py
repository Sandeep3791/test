from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea,ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models_orders import Orders,OrderStatus
from django.forms import ModelForm

class OrderStatusUpdatedForm(ModelForm):
    status=forms.ChoiceField(required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        order_choices=[(get_users_options.pk,get_users_options.name) for get_users_options in OrderStatus.objects.filter()]
        self.fields['status'].choices=order_choices
        #self.fields['status'].queryset = OrderStatus.objects

    class Meta:
        model = Orders
        fields =['status']