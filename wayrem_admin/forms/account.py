from django import forms
from wayrem_admin.models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class DateInput(forms.DateInput):
    input_type = 'date'


class SubAdminForm(UserCreationForm):

    error_messages = {
        "password_mismatch": "Password and Confirm Password should be same"
    }

    password1 = forms.CharField(label='Password',
                                widget=forms.HiddenInput(attrs={'class': 'form-control eye'}))
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.HiddenInput(attrs={'class': 'form-control eye'}))

    class Meta:
        model = CustomUser
        fields = ("username", "email", "contact", "role")

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control', 'minlength': 10}),
            'role': forms.Select(attrs={'class': 'form-select'})
            # 'role': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SubAdminUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "contact", "role")

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control', 'minlength': 10}),
            'role': forms.Select(attrs={'class': 'form-select'})
        }


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
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}, render_value=True),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}, render_value=True),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}, render_value=True),
    )
