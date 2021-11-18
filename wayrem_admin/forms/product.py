from django import forms
from wayrem_admin.models import Supplier, Categories, Ingredients, Products
from datetime import datetime


class DateInput(forms.DateInput):
    input_type = 'date'


class ProductFormOne(forms.Form):
    SKU = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control"}))
    product_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    product_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    feature_product = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    product_deliverable = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': "form-check-input"}), required=False)
    date_of_mfg = forms.DateField(
        widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    date_of_exp = forms.DateField(
        widget=DateInput(attrs={'class': 'form-control'}))
    mfr_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control"}))
    # supplier_name = forms.CharField()

    def get_category():
        obj = Categories.objects.all()
        choice = [(r.id, r.name) for r in obj]
        return choice

    choices_category = get_category

    def get_supplier():
        obj = Supplier.objects.all()
        choice = [(r.id, r.username) for r in obj]
        return choice

    choices_role = get_supplier

    # supplier_name = forms.CharField()
    product_category = forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
        attrs={'class': 'form-control'}), required=False)
    supplier_name = forms.MultipleChoiceField(
        choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)

    def clean(self):
        form_data = self.cleaned_data
        if "date_of_exp" and "date_of_mfg" in form_data and form_data['date_of_exp'] < form_data['date_of_mfg']:
            # Will raise a error message
            self._errors["date_of_exp"] = "Invalid Date"
            del form_data['date_of_mfg']
        return form_data
    # def clean(self):
    #     cleaned_data = super(ProductFormOne, self).clean()
    #     date_of_mfg = cleaned_data.get("date_of_mfg")
    #     date_of_exp = cleaned_data.get("date_of_exp")

    #     if date_of_mfg != date_of_exp:
    #         raise forms.ValidationError(
    #             "Manufacture date should be different!"
    #         )
    #     return cleaned_data


class ProductFormTwo(forms.Form):
    product_weight = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    UNIT_CHOICES = (
        ('GRAM', 'gm'),
        ('KILO-GRAM', 'kg'),
        ('MILLI-LITRE', 'ml'),
        ('LITRE', 'ltr'),
    )
    unit = forms.ChoiceField(choices=UNIT_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    discount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    DIS_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    dis_abs_percent = forms.ChoiceField(
        choices=DIS_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    wayrem_margin = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    WAYREM_ABS_PERCENT = (
        ('(Absolute ', 'Abs'),
        ('%', '%'),
    )
    wayrem_abs_percent = forms.ChoiceField(
        choices=WAYREM_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    package_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))
    product_meta_key = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}))


class ProductFormThree(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}), required=False)
    calories1 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}), required=False)
    calories2 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}), required=False)
    calories3 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}), required=False)
    calories4 = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}), required=False)
    # nutrition = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    product_qty = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': "form-control"}))

    def get_ingredients():
        obj = Ingredients.objects.all()
        choice = [(None, "Select Ingredients")]
        ch = [(r.id, r.ingredients_name) for r in obj]
        choice.extend(ch)
        print(choice)
        return choice

    choices_role = get_ingredients

    ingredients1 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    ingredients2 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    ingredients3 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    ingredients4 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)


class ProductFormFour(forms.Form):
    # wayrem_margin = forms.IntegerField(
    #     widget=forms.NumberInput(attrs={'class': "form-control"}))
    # WAYREM_ABS_PERCENT = (
    #     ('(Absolute ', 'Abs'),
    #     ('%', '%'),
    # )
    # wayrem_abs_percent = forms.ChoiceField(
    #     choices=WAYREM_ABS_PERCENT, widget=forms.Select(attrs={'class': 'form-select'}))
    image1 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}))
    image2 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}))
    image3 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}))
    image4 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}), required=False)
    image5 = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}), required=False)


class ProductUpdateForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = ("SKU", "product_category", "product_code", "product_meta_key",
                  "feature_product", "product_deliverable", "date_of_mfg", "date_of_exp", "mfr_name", "supplier_name", "dis_abs_percent",
                  "image1", "image2", "image3", "image4", "image5", "product_name",
                  "description", "ingredients1", "ingredients2", "ingredients3", "ingredients4",
                  "calories1", "calories2", "calories3", "calories4", "product_qty", "product_weight",
                  "unit", "price", "discount", "package_count", "wayrem_margin", "wayrem_abs_percent")

        widgets = {
            'SKU': forms.TextInput(attrs={'class': "form-control"}),
            'product_name': forms.TextInput(attrs={'class': "form-control"}),
            'product_code': forms.TextInput(attrs={'class': "form-control"}),
            'feature_product': forms.CheckboxInput(attrs={'class': "form-check-input", 'required': False}),
            'product_deliverable': forms.CheckboxInput(attrs={'class': "form-check-input", 'required': False}),
            'date_of_mfg': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exp': DateInput(attrs={'class': 'form-control'}),
            'mfr_name': forms.TextInput(attrs={'class': "form-control"}),
            'product_weight': forms.NumberInput(attrs={'class': "form-control"}),
            'price': forms.NumberInput(attrs={'class': "form-control"}),
            'discount': forms.NumberInput(attrs={'class': "form-control"}),
            'wayrem_margin': forms.NumberInput(attrs={'class': "form-control"}),
            'package_count': forms.NumberInput(attrs={'class': "form-control"}),
            'product_meta_key': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '3'}),
            'calories1': forms.NumberInput(attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}),
            'calories2': forms.NumberInput(attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}),
            'calories3': forms.NumberInput(attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}),
            'calories4': forms.NumberInput(attrs={'class': "form-control", 'step': 0.1, 'placeholder': 'Calories (kcal)'}),
            'product_qty': forms.NumberInput(attrs={'class': "form-control"}),
            'image1': forms.FileInput(attrs={'class': "form-control-file"}),
            'image2': forms.FileInput(attrs={'class': "form-control-file"}),
            'image3': forms.FileInput(attrs={'class': "form-control-file"}),
            'image4': forms.FileInput(attrs={'class': "form-control-file", 'required': False}),
            'image5': forms.FileInput(attrs={'class': "form-control-file", 'required': False}),
            'product_category': forms.SelectMultiple(attrs={'class': 'form-control', 'required': False}),
            'supplier_name': forms.SelectMultiple(attrs={'class': 'form-control', 'required': False}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'dis_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'wayrem_abs_percent': forms.Select(attrs={'class': 'form-select'}),
            'ingredients1': forms.Select(attrs={'class': 'form-select'}),
            'ingredients2': forms.Select(attrs={'class': 'form-select'}),
            'ingredients3': forms.Select(attrs={'class': 'form-select'}),
            'ingredients4': forms.Select(attrs={'class': 'form-select'})
        }
