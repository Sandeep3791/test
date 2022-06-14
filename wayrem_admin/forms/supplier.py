from django import forms
from wayrem_admin.models import Supplier


def validate_digits_letters(word):
    for char in word:
        if not char.isdigit() and not char.isalpha():
            return False
    return True


class SupplierForm(forms.ModelForm):
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.HiddenInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Supplier
        fields = ("username", "email", "password",
                  "category_name", "company_name", "address")

        # role = forms.MultipleChoiceField(choices=Roles)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # 'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            'password': forms.HiddenInput(attrs={'class': 'form-control'}),
            'category_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
        error_messages = {
            'username': {
                'unique': "This username is already taken.",
            },
        }

    def clean(self):
        cleaned_data = super(SupplierForm, self).clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError(
                "Password and Confirm Password should be same."
            )
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username.islower():
            raise forms.ValidationError("Username should be in lowercase")

        if not validate_digits_letters(username):
            raise forms.ValidationError(
                "Username should not contain special characters")

        if ' ' in username:
            raise forms.ValidationError(
                'username should not contain any space')
        return username


class SupplierUpdateForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ("username", "email", "category_name",
                  "company_name", "address")

        # role = forms.MultipleChoiceField(choices=Roles)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'category_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username:
            raise forms.ValidationError(
                'username should not contain any space')
        return username


class SupplierSearchFilter(forms.Form):
    supplier = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)


class SupplierInvoiceSearchFilter(forms.Form):
    supplier_invoice = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
