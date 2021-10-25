from enum import unique
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db import models
from django.db.models.base import Model
from django.forms import widgets
from django.http import request
from .models import CustomUser, Roles
from django.core.exceptions import ValidationError


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models.query import QuerySet
from django.forms import widgets
from django.forms.fields import MultipleChoiceField
from .models import *


class SubAdminForm(UserCreationForm):

    def choice():
        obj = Roles.objects.all()
        choice = [(r.id, r.role) for r in obj]
        return choice

    contact = forms.CharField(label='Contact',
                              widget=forms.NumberInput(attrs={'class': 'form-control'}), required=True)

    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    choices_role = choice

    role = forms.ChoiceField(choices=choices_role, widget=forms.Select(
        attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ("username", "email", "contact")

        # role = forms.MultipleChoiceField(choices=Roles)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'role': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DateInput(forms.DateInput):
    input_type = 'date'


class ProfileUpdateForm(forms.ModelForm):
    dob = forms.DateField(widget=DateInput(attrs={'class': 'form-select'}))

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "contact",
                  "gender", "role", "dob", "address", "city", "zip_code")

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # 'dob': forms.DateInput(attrs={'class': 'form-control','class':DateInput()}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            # 'gender' : forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'})),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'role': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ("name", "category_image", "description")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'category_image': forms.ImageField(attrs={'class': 'form-control-file'}),
            # 'category_image': forms.FieldInput(widget=forms.FileInput(attrs={'class': 'rounded_list'})),
            'category_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }


# class ProductForm(forms.ModelForm):

#     def get_category():
#         obj = Categories.objects.all()
#         choice = [(r.id, r.name) for r in obj]
#         return choice

#     choices_role = get_category

#     category = forms.ChoiceField(choices=choices_role, widget=forms.Select(
#         attrs={'class': 'form-select'}))

#     class Meta:
#         model = Products
#         fields = ("name", "image", "price", "quantity",
#                   "weight", "description", "provider")

#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control rounded-right', }),
#             # 'category': forms.Select(attrs={'class': 'form-select'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control', }),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control', }),
#             'weight': forms.NumberInput(attrs={'class': 'form-control', }),
#             'description': forms.TextInput(attrs={'class': 'form-control', }),
#             'provider': forms.TextInput(attrs={'class': 'form-control', }),
#             'contact': forms.NumberInput(attrs={'class': 'form-control', }),
#         }


# class ProductUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Products
#         fields = ("id", "name", "image", "category", "price",
#                   "quantity", "weight", "description", "provider")


class SupplierRegisterForm(forms.ModelForm):
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SupplierRegister
        fields = ("username", "email", "password", "category_name")

        # role = forms.MultipleChoiceField(choices=Roles)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # 'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'category_name': forms.SelectMultiple(attrs={'class': 'form-control'})
            # 'role': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super(SupplierRegisterForm, self).clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError(
                "password and confirm password does not match"
            )
        return cleaned_data


class RoleForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Add Role Description...'}))

    class Meta:
        model = Roles
        fields = ('role', 'status', 'content', 'permission')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.required:
                visible.field.widget.attrs['class'] = 'form-control required-cls'
            else:
                visible.field.widget.attrs['class'] = 'form-control'


class RoleViewForm(forms.ModelForm):

    class Meta:
        model = Roles
        fields = ('permission',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.required:
                # visible.field.widget.attrs['class'] = 'form-control required-cls'
                visible.field.widget.attrs['readonly'] = True
            else:
                visible.field.widget.attrs['class'] = 'form-control'
                visible.field.widget.attrs['readonly'] = True


class ProductFormOne(forms.Form):
    SKU = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control"}))
    product_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    product_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    feature_product = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    product_deliverable = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    date_of_mfg = forms.DateField(
        widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    date_of_exp = forms.DateField(
        widget=DateInput(attrs={'class': 'form-control'}))
    mfr_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    # supplier_name = forms.CharField()

    def get_category():
        obj = Categories.objects.all()
        choice = [(r.id, r.name) for r in obj]
        return choice

    choices_category = get_category

    def get_supplier():
        obj = SupplierRegister.objects.all()
        choice = [(r.id, r.username) for r in obj]
        return choice

    choices_role = get_supplier

    # supplier_name = forms.CharField()
    product_category = forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
        attrs={'class': 'form-control'}), required=False)
    supplier_name = forms.MultipleChoiceField(
        choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)

    # def get_category():
    #     obj = Categories.objects.all()
    #     choice = [(r.id, r.name) for r in obj]
    #     return choice

    # choices_role = get_category

    # category = forms.ChoiceField(choices=choices_role, widget=forms.Select(
    #     attrs={'class': 'form-select'}))


class ProductFormTwo(forms.Form):
    product_weight = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    UNIT_CHOICES = (
        ('GRAM', 'gm'),
        ('KILO-GRAM', 'kg'),
        ('MILLI-LITRE', 'ml'),
        ('LITRE', 'ltr'),
    )
    unit = forms.ChoiceField(choices=UNIT_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    discount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    DIS_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    dis_abs_percent = forms.ChoiceField(
        choices=DIS_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    package_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    product_meta_key = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))


class ProductFormThree(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}))
    calories1 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}))
    calories2 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}))
    calories3 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}))
    calories4 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}))
    # nutrition = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    product_qty = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))

    def get_ingredients():
        obj = Ingredients.objects.all()
        choice = [(r.id, r.ingredients_name) for r in obj]
        return choice

    choices_role = get_ingredients

    ingredients1 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients2 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients3 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients4 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))


class ProductFormFour(forms.Form):
    wayrem_margin = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    WAYREM_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    wayrem_abs_percent = forms.ChoiceField(
        choices=WAYREM_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    image1 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control"}))
    image2 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control"}))
    image3 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control"}))
    image4 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control"}))
    image5 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control"}))


class IngredientsCreateForm(forms.ModelForm):
    class Meta:
        model = Ingredients
        fields = ("ingredients_name", "ingredients_status",)

        widgets = {
            'ingredients_name': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients_status': forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'})),
        }


# class PurchaseOrderCreateForm(forms.ModelForm):
#     class Meta:
#         model = PurchaseOrderPO
#         fields = ("product_name", "product_name", "price", "supplier_name",)

#         widgets = {
#             'product_name': forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
#         attrs={'class': 'form-control'}), required=False)
#         'supplier_name' = forms.MultipleChoiceField(
#         choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)
#             'product_name': forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'})),
#         }


# class PurchaseOrderCreateForm(forms.Form):

#     def get_category():
#         obj = Products.objects.all()
#         choice = [(r.id, r.name) for r in obj]
#         return choice

#     choices_category = get_category

#     def get_supplier():
#         obj = SupplierRegister.objects.all()
#         choice = [(r.id, r.username) for r in obj]
#         return choice

#     choices_role = get_supplier

#     # supplier_name = forms.CharField()
#     product_category = forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
#         attrs={'class': 'form-control'}), required=False)
#     supplier_name = forms.MultipleChoiceField(
#         choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)
