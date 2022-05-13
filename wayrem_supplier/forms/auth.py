from django import forms
from wayrem_supplier.models import Supplier


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
