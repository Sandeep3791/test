from django import forms
from wayrem_admin.models.users import Users


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
        model = Users
        fields = ("username", "email", "contact", "role",
                  "po_notify", "order_notify", "margin_access")

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control', 'minlength': 10}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'po_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'margin_access': forms.CheckboxInput(attrs={'class': 'form-check-input'})
            # 'role': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'username': {
                'unique': "This username is already taken.",
            },
        }


class SubAdminUpdateForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = ("username", "email", "contact", "role",
                  "po_notify", "order_notify", "margin_access")

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control', 'minlength': 10}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'po_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order_notify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'margin_access': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ProfileUpdateForm(forms.ModelForm):
    # dob = forms.DateField(widget=DateInput(
    #     attrs={'class': 'form-control datepicker-input'}))

    class Meta:
        model = Users
        fields = ("first_name", "last_name", "email", "contact",
                  "gender", "role", "dob", "address", "city", "zip_code")

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control datepicker-input', 'placeholder': "dd/mm/yyyy", 'type': 'date'}),
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


class UserSearchFilter(forms.Form):
    user = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
