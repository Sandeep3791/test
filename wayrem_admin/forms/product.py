from django import forms
from wayrem_admin.forms import DateInput
from wayrem_admin.models import SupplierRegister, Categories


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
        obj = SupplierRegister.objects.all()
        choice = [(r.id, r.username) for r in obj]
        return choice

    choices_role = get_supplier

    # supplier_name = forms.CharField()
    product_category = forms.MultipleChoiceField(choices=choices_category, widget=forms.SelectMultiple(
        attrs={'class': 'form-control'}), required=False)
    supplier_name = forms.MultipleChoiceField(
        choices=choices_role, widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)

    # def get_category():
    #     obj = Categories.objects.all()
    #     choice = [(r.id, r.name) for r in obj]
    #     return choice

    # choices_role = get_category

    # category = forms.ChoiceField(choices=choices_role, widget=forms.Select(
    #     attrs={'class': 'form-select'}))


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
        choice = [(r.id, r.ingredients_name) for r in obj]
        return choice

    choices_role = get_ingredients

    ingredients1 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients2 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients3 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))
    ingredients4 = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}))


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
