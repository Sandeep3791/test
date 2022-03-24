from django import forms
from wayrem_admin.models import PurchaseOrder, Supplier, SupplierProducts


class POForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ("product_name", "product_qty", "supplier_name")

        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': "form-control", 'max': 1000}),
            'supplier_name': forms.Select(attrs={'class': 'form-select'})
        }


class POFormOne(forms.Form):
    product_name = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-select'}))
    supplier_name = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}))
    product_qty = forms.CharField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'max': 1000}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        supplier_choices = [(supplier.pk, supplier.company_name)
                            for supplier in Supplier.objects.all()]
        product_choices = [(prod.pk, prod.product_name + "(SKU:"+prod.SKU+")")
                           for prod in SupplierProducts.objects.all()]
        supplier_choices.insert(0, ('', 'Select Supplier'))
        product_choices.insert(0, ('', 'Select Product'))
        self.fields['supplier_name'].choices = supplier_choices
        self.fields['product_name'].choices = product_choices


class POEditForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ("product_name", "product_qty")

        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': "form-control"}),
        }


class POSearchFilter(forms.Form):
    po = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
