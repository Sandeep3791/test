from django.forms import (
    formset_factory, modelformset_factory, BaseModelFormSet)
from django import forms
from wayrem_admin.models import ProductIngredients, Supplier, Categories, Images, Ingredients, Products, UNIT_CHOICES, DIS_ABS_PERCENT, Unit
from datetime import datetime


class DateInput(forms.DateInput):
    input_type = 'date'


class ProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = ("name", "SKU", "category", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "quantity_unit", "weight", "weight_unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            # 'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.CheckboxInput(attrs={'class': "form-check-input"}),
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
        attrs={'class': 'form-control-select', 'multiple': True}), required=False)


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
        fields = ("name", "SKU", "category", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "quantity_unit", "weight", "weight_unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit", "primary_image")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            # 'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'wayrem_margin': forms.NumberInput(attrs={'class': "form-control"}),
            'margin_unit': forms.Select(attrs={'class': 'form-select'}),
            'primary_image': forms.FileInput(attrs={'class': "form-control-file"}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'supplier': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ProductFormImageView(forms.ModelForm):

    class Meta:
        model = Products
        fields = ("name", "SKU", "category", "meta_key", "feature_product", "publish", "date_of_mfg", "date_of_exp", "mfr_name", "supplier",
                  "dis_abs_percent", "description", "quantity", "quantity_unit", "weight", "weight_unit", "price", "discount", "package_count", "wayrem_margin", "margin_unit", "primary_image")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'SKU': forms.TextInput(attrs={'class': 'form-control'}),
            # 'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'publish': forms.CheckboxInput(attrs={'class': "form-check-input"}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mfr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_unit': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_unit': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.CheckboxInput(attrs={'class': "form-check-input"}),
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

# Product Create Form


def get_category():
    obj = Categories.objects.all()
    choice = [(r.id, r.name + " - " + str(r.margin)+r.unit) for r in obj]
    return choice


choices_category = get_category


def get_supplier():
    obj = Supplier.objects.all()
    choice = [(r.id, r.company_name) for r in obj]
    return choice


choices_role = get_supplier


def get_unit():
    obj = Unit.objects.all()
    choice = [(r.id, r.unit_name) for r in obj]
    return choice


choices_unit = get_unit


class ProductFormOne(forms.Form):
    SKU = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control"}))
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    feature_product = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    publish = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    date_of_mfg = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker-input', 'placeholder': "dd/mm/yyyy", 'type': 'date'}))
    date_of_exp = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control datepicker-input', 'placeholder': "dd/mm/yyyy", 'type': 'date'}))
    mfr_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    category = forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
        attrs={'class': 'form-control'}), required=False)
    supplier = forms.MultipleChoiceField(
        choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)
    weight = forms.CharField(
        widget=forms.NumberInput(attrs={'class': "form-control", 'min': 0, 'step': '0.001'}))
    weight_unit = forms.ChoiceField(choices=choices_unit, widget=forms.Select(
        attrs={'class': 'form-select'}))
    price = forms.CharField(
        widget=forms.NumberInput(attrs={'class': "form-control", 'min': 1, 'step': '0.01'}))
    discount = forms.CharField(
        widget=forms.NumberInput(attrs={'class': "form-control", 'min': 0}))
    dis_abs_percent = forms.ChoiceField(
        choices=DIS_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    wayrem_margin = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control", 'min': 0}), min_value=0)
    margin_unit = forms.ChoiceField(
        choices=DIS_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    package_count = forms.CharField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    meta_key = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}), required=False)
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}), min_value=0)
    quantity_unit = forms.ChoiceField(choices=choices_unit, widget=forms.Select(
        attrs={'class': 'form-select'}))

    def clean_date_of_exp(self):
        cleaned_data = super(ProductFormOne, self).clean()
        try:
            dom = cleaned_data.get("date_of_mfg")
            doe = cleaned_data.get("date_of_exp")

            if dom >= doe:
                raise forms.ValidationError(
                    f"Date of expiry must be greater than {dom}"
                )
            else:
                return doe
        except:
            pass

    def clean_SKU(self):
        SKU = self.cleaned_data.get("SKU")
        if Products.objects.filter(SKU=SKU).exists():
            raise forms.ValidationError("SKU already Exists!")
        return SKU
