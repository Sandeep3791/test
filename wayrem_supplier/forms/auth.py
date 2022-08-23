from django.contrib.auth import password_validation
from django import forms
from wayrem_supplier.models import Supplier, OtpDetails


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = ("email", "logo", "contact", "address", "delivery_incharge", "company_name", "first_name", "last_name",
                  "company_phone_no", "company_email", "registration_no", "contact_person_name", "contact_phone_no", "from_time", "to_time")

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'contact': forms.NumberInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_incharge': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control'}),
            'from_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone_no': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ResetPasswordForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}), required=False
    )
    otp = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'autofocus': True}), required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}, render_value=True),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control'}, render_value=True),
    )

    def clean_new_password(self):
        email = self.cleaned_data.get('email')
        user = Supplier.objects.get(email=email)
        password = self.cleaned_data.get("new_password")
        password_validation.validate_password(password, user)
        return password

    def clean_confirm_password(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        password = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")

        if password != password2:
            raise forms.ValidationError(
                "The two password fields didn't match."
            )
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not Supplier.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Doesn't Exist!")
        return email

    def clean_otp(self):
        email = self.cleaned_data.get("email")
        otp = self.cleaned_data.get("otp")
        if not OtpDetails.objects.filter(email=email, otp=otp).exists():
            raise forms.ValidationError("Incorrect Otp!")
        return email
