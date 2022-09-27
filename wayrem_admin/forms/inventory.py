from django.forms import Textarea, ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models import Inventory, InventoryType
from wayrem_admin.models import Products, Categories


def get_products():
    obj = Products.objects.all()
    choice = [(r.id, r.SKU + " - " + r.name) for r in obj]
    return choice


choices_products = get_products


class InventoryForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Products.objects.all(
    ), empty_label=None, widget=forms.Select(attrs={'class': 'form-select'}))
    inventory_type = forms.ModelChoiceField(queryset=InventoryType.objects.filter(
        id__in=[1, 5]), empty_label=None, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super(InventoryForm, self).__init__(*args, **kwargs)
        self.fields['product'].label_from_instance = lambda instance: instance.SKU + \
            " - " + instance.name

    class Meta:
        model = Inventory
        fields = ("product", "quantity", 'inventory_type', 'description')
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '0', 'step': '1', 'class': 'form-control'}),
        }


class InventoryViewForm(forms.ModelForm):
    product = forms.ChoiceField(choices=choices_products, widget=forms.Select(
        attrs={'class': 'form-select', 'readonly': 'true'}))

    get_inventory_type_dict = {0: 'Starting', 1: 'Received', 2: 'Shipped'}
    get_inventory_type_dict = {
        1: 'Starting', 2: 'Received', 3: 'Shipped', 4: 'Cancelled', 5: 'Removed'}
    inventory_type_choices = list(get_inventory_type_dict.items())
    inventory_type = forms.ChoiceField(
        choices=inventory_type_choices, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.fields['inventory_type'].widget.attrs['readonly'] = True

    class Meta:
        model = Inventory
        fields = ("product", "quantity", 'inventory_type')
        readonly_fields = ["product"]
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '0', 'step': '1', 'class': 'form-control'}),
        }


class InventoryAdvanceFilterForm(forms.Form):
    category = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2', 'placeholder': 'Product name'}), required=False)
    mfr_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2', 'placeholder': 'Brand'}), required=False)
    customer = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2', 'placeholder': 'Customer'}), required=False)
    SKU = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2', 'placeholder': 'SKU'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        category_choice = [(get_users_options.pk, get_users_options.name)
                           for get_users_options in Categories.objects.filter()]
        category_choice.insert(0, ('', 'Select Category'))
        self.fields['category'].choices = category_choice
