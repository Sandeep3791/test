from django.forms import Textarea,ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models import Warehouse


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ("address", "status", "code_name")
        widgets = {
            'code_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': Textarea(attrs={'cols':3, 'rows':3}),
        }

class WarehouseViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        model = Warehouse
        fields = ("address", "status", "code_name")
        widgets = {
            'code_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': Textarea(attrs={'cols':3, 'rows':3}),
        }

