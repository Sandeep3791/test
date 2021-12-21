from django import forms
from wayrem_admin.models import Supplier


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


class SupplierUpdateForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ("username", "email", "category_name",
                  "company_name", "address")

        # role = forms.MultipleChoiceField(choices=Roles)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'category_name': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
