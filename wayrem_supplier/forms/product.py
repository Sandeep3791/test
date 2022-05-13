from django import forms
from wayrem_supplier.models import SupplierProducts


class SupplierProductForm(forms.ModelForm):
    
    class Meta:
        model = SupplierProducts
        fields = ("SKU","product_name", "quantity", "price", "available", "deliverable_days","supplier_id")

        widgets = {
            'SKU': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'product_name': forms.TextInput(attrs= {'class': 'form-control', 'readonly': 'readonly'}),
            'quantity': forms.NumberInput(attrs= {'class':'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs= {'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'available': forms.CheckboxInput(attrs= {'class': 'form-check-input'}),
            'deliverable_days': forms.Select(attrs= {'class': 'form-control, form-select'}),
            'supplier_id': forms.HiddenInput(attrs= {'class': 'form-control'}),

        }