from django.forms import (
    formset_factory, modelformset_factory, BaseModelFormSet)
from django import forms
from wayrem_admin.models import ProductIngredients, Supplier, Categories, Images, Ingredients, Products
from datetime import datetime


class DateInput(forms.DateInput):
    input_type = 'date'


class ProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = ("name", "SKU", "category", "product_code", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "weight", "unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.NumberInput(attrs={'class': "form-control"}),
            'wayrem_margin': forms.NumberInput(attrs={'class': "form-control"}),
            'margin_unit': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'supplier': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ProductImageForm(forms.Form):
    primary_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-select'}))
    images = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control-select', 'multiple': True}))


class ProductImgUpdateForm(forms.Form):
    images = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control-select', 'multiple': True}),required=False)


class ProductIngredientForm(forms.ModelForm):

    class Meta:
        model = ProductIngredients
        fields = ("ingredient", "quantity", "unit")

        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }


class BaseProductIngredients(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseProductIngredients, self).__init__(*args, **kwargs)
        self.queryset = ProductIngredients.objects.none()


# ProductIngredientFormset1 = formset_factory(ProductIngredientForm, extra=0)
ProductIngredientFormset = modelformset_factory(
    ProductIngredients,
    fields=("ingredient", "quantity", "unit"),
    extra=1,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-select select_ingrid x', 'placeholder': 'select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control form-control', 'placeholder': 'Quantity'}),
        'unit': forms.Select(attrs={'class': 'form-select select_unit'}),
    },
    formset=BaseProductIngredients
)

ProductIngredientFormset1 = modelformset_factory(
    ProductIngredients,
    fields=("ingredient", "quantity", "unit"),
    extra=0,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-select select_ingrid x', 'placeholder': 'select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control form-control', 'placeholder': 'Quantity'}),
        'unit': forms.Select(attrs={'class': 'form-select select_unit'}),
    },

)

ProductIngredientFormsetView = modelformset_factory(
    ProductIngredients,
    fields=("ingredient", "quantity", "unit"),
    extra=0,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-select', 'disabled': True, 'placeholder': 'select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': 'Quantity'}),
        'unit': forms.Select(attrs={'class': 'form-select', 'disabled': True}),
    }
)


class ProductFormView(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductFormView, self).__init__(*args, **kwargs)
        # self.fields['field'].widget.attrs['readonly'] = True
        # self.fields.widgets.attrs['readonly'] = True
        for field in self.fields:
            self.fields[field].disabled = True

    class Meta:
        model = Products
        fields = ("name", "SKU", "category", "product_code", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "weight", "unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit", "primary_image")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.NumberInput(attrs={'class': "form-control"}),
            'wayrem_margin': forms.NumberInput(attrs={'class': "form-control"}),
            'margin_unit': forms.Select(attrs={'class': 'form-select'}),
            'primary_image': forms.FileInput(attrs={'class': "form-control-file"}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'supplier': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ProductFormImageView(forms.ModelForm):

    class Meta:
        model = Products
        fields = ("name", "SKU", "category", "product_code", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "weight", "unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit", "primary_image")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.NumberInput(attrs={'class': "form-control"}),
            'wayrem_margin': forms.NumberInput(attrs={'class': "form-control"}),
            'margin_unit': forms.Select(attrs={'class': 'form-select'}),
            'primary_image': forms.FileInput(attrs={'class': "form-control-file"}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'supplier': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


ProductImageFormset = modelformset_factory(
    Images,
    fields=("image",),
    extra=0,
    widgets={
        'image':  forms.FileInput(attrs={'class': 'form-control-select'}),
    },

)
