from django import forms
from wayrem_admin.models import PurchaseOrder


class POForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ("product_name", "product_qty", "supplier_name")

        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': "form-control", 'max': 1000}),
            'supplier_name': forms.Select(attrs={'class': 'form-select'})
        }


class POEditForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ("product_name", "product_qty")

        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': "form-control"}),
        }
