from django import forms
from wayrem_admin.models.StaticModels import CreditSettings, Customer


class CustomerSearchFilter(forms.Form):
    customer = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)


class CustomerEmailUpdateForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ("email",)

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CreditsForm(forms.ModelForm):
    class Meta:
        model = CreditSettings
        fields = ("credit_amount", "time_period")
        widgets = {
            'credit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_period': forms.NumberInput(attrs={'class': 'form-control'})
        }


class CreditsSearchFilter(forms.Form):
    credit = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control p-2'}), required=False)
