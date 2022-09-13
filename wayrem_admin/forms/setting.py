from django import forms
from django.forms import widgets
from wayrem_admin.models import Settings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ("key", "display_name", "type")

        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control form-select'}),
        }


class SettingSearchFilter(forms.Form):
    settings = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2', 'placeholder': 'Search'}), required=False)
