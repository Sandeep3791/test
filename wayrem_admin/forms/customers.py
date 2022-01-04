from django import forms


class CustomerSearchFilter(forms.Form):
    customer = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
