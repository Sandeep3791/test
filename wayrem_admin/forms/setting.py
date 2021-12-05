from django import forms
from django.forms import widgets
from wayrem_admin.models import Settings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ("key", "display_name", "type")

        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form--control-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
