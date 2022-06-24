from django import forms
from wayrem_admin.models import CreditSettings, Customer


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


def get_credits():
    obj = CreditSettings.objects.all()
    choice = [(None, "Select Credit Rule")]
    ch = [(r.id, r.credit_amount) for r in obj]
    choice.extend(ch)
    print(choice)
    return choice


class CreditsAssignForm(forms.Form):
    credit = forms.ChoiceField(choices=get_credits, widget=forms.Select(
        attrs={'class': 'form-select'}), required=False)

    def clean_credit(self):
        cleaned_data = super(CreditsAssignForm, self).clean()
        credit = cleaned_data.get("credit")
        if credit == None or credit == "":
            raise forms.ValidationError(
                f"Please select a Credit amount!"
            )
        else:
            return credit
