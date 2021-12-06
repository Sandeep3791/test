import json
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import Products
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from wayrem_admin.services import *
from wayrem_admin.export import generate_excel, generate_pdf
from wayrem_admin.forms import *
from wayrem_admin.decorators import role_required
import biip
from django.forms import formset_factory


def product_excel(request):
    return generate_excel("products_master", "products")


def pdf_product(request):
    query = 'SELECT  SKU, product_code, product_meta_key, feature_product, product_deliverable, date_of_mfg, date_of_exp, mfr_name, dis_abs_percent, image1, image2, image3, image4, image5, product_name, description, ingredients1_id, ingredients2_id, ingredients3_id, ingredients4_id, calories1, calories2, calories3, calories4, nutrition, product_qty, product_weight, unit, price, discount, package_count, wayrem_margin, wayrem_abs_percent FROM products_master'
    template = "pdf_product.html"
    file = "products.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


@role_required('Products Add')
def product(request):
    if request.method == "POST":
        delSession(request)
        user_code = request.POST.get('code')
        user_code = user_code.replace('\\x1d', '\x1d')
        try:
            result = biip.parse(user_code)
            request.session['SKU'] = result.gs1_message.element_strings[0].value
            request.session['price'] = str(
                result.gs1_message.element_strings[5].decimal)
            request.session['date_of_exp'] = str(
                result.gs1_message.element_strings[1].date)
            request.session['weight'] = str(
                result.gs1_message.element_strings[4].decimal)
            request.session['unit'] = "KILO-GRAM"
            request.session['gs1'] = user_code
        except:
            pass
        return redirect('wayrem_admin:productviewone')
    delSession(request)
    return render(request, 'inputBar.html')


def details_gs1(request):
    delSession(request)
    user_code = request.GET.get('barcode')
    user_code = user_code.replace('\\x1d', '\x1d')
    try:
        result = biip.parse(user_code)
        request.session['gs1'] = user_code
        request.session['SKU'] = result.gs1_message.element_strings[0].value
        request.session['price'] = str(
            result.gs1_message.element_strings[5].decimal)
        request.session['date_of_exp'] = str(
            result.gs1_message.element_strings[1].date)
        request.session['weight'] = str(
            result.gs1_message.element_strings[4].decimal)
        request.session['unit'] = "KILO-GRAM"
    except:
        pass
    data = [request.session.get('SKU'), request.session.get(
        'price'), request.session.get('date_of_exp'), request.session.get('weight'), request.session.get('unit')]
    return render(request, 'barcode_details.html', {'data': data})


def inputBar(request):
    delSession(request)
    return redirect('wayrem_admin:product')


def load_supplier(request):
    x = dict(request.GET)
    category = x.get('category_product[]')

    supplier = [Supplier.objects.filter(
        category_name=i).all() for i in category]
    # supplier = Supplier.objects.filter(category_name=category).all()
    return render(request, 'supplier_dropdown.html', {'supplier': supplier})


def load_category_margin(request):
    x = dict(request.GET)
    category = x.get('cat_margin[]')

    category_obj = [Categories.objects.filter(
        pk=i).all() for i in category]
    category = category_obj[0][0]
    margin = category.margin
    unit = category.unit
    data = json.dumps({
        'margin': margin,
        'unit': unit,
    })
    # supplier = Supplier.objects.filter(category_name=category).all()
    return HttpResponse(data, content_type='application/json')


@role_required('Products Add')
def product_view_one(request):
    # date_of_mfg = datetime.date(json.loads(
    #     request.session.get('date_of_exp')), "%Y-%m-%d")
    # date_of_exp = datetime.strptime(json.loads(
    #     request.session.get('date_of_exp')), "%Y-%m-%d").date(),

    initial = {
        'SKU': request.session.get('SKU', None),
        'product_category': request.session.get('product_category', None),
        'product_code': request.session.get('product_code', None),
        'product_name': request.session.get('product_name', None),
        'feature_product': request.session.get('feature_product', None),
        'unit': request.session.get('unit', None),
        'date_of_mfg': request.session.get('date_of_mfg', None),
        'date_of_exp': request.session.get('date_of_exp', None),
        'price': request.session.get('price', None),
        'weight': request.session.get('weight', None),
    }
    context = {}
    form = ProductForm(request.POST, initial=initial)
    formset = ProductIngredientFormset(request.POST)
    context['form'] = form
    context['formset'] = formset
    if request.method == 'POST':
        print("Post")
        print(formset.is_valid())
        print(formset.errors)
        print(form.is_valid())
        if form.is_valid() and formset.is_valid():
            product_id = uuid.uuid4()
            product = form.save(commit=False)
            product.id = product_id
            product.save()
            for form in formset.forms:
                obj = ProductIngredients()
                obj.product = product_id
                obj.ingredient = form.cleaned_data.get('ingredient')
                obj.quantity = form.cleaned_data.get('quantity')
                obj.unit = form.cleaned_data.get('unit')
                obj.save()
            request.session['product_pk'] = str(product_id)
            return redirect('wayrem_admin:product_images')
            # return HttpResponse(render(request,'path_to_your_view.html'))
    else:
        context['form'] = ProductForm(initial=initial)
        # context['formset'] = formset_factory(ProductIngredientForm, extra=1)
        context['formset'] = ProductIngredientFormset()
    return render(request, 'product1.html', context)


@role_required('Products Add')
def product_images(request):
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            obj_id = request.session.get('product_pk')
            obj = Products.objects.get(id=obj_id)
            primary_image = request.FILES.get('primary_image', None)
            obj.primary_image = primary_image
            obj.save()
            images = request.FILES.getlist('images')
            for image in images:
                img_obj = Images()
                img_obj.image = image
                img_obj.product = obj
                img_obj.save()
            return redirect('wayrem_admin:productlist')

    else:
        form = ProductImageForm()
    return render(request, "product4.html", {'form': form})
# # ----------------------------------------------------------------------------


class ProductList(View):
    template_name = "productlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Products View'))
    def get(self, request, format=None):
        productslist = Products.objects.all()
        return render(request, self.template_name, {"productslist": productslist})


@role_required('Product View')
def product_details(request, id=None):
    prod = Products.objects.filter(id=id).first()
    return render(request, 'View_product.html', {'proddata': prod})


@role_required('Products Edit')
def update_product(request, id=None, *args, **kwargs):
    # print(id)

    ingrd = ProductIngredients.objects.filter(product=id).all()
    prod = Products.objects.get(id=id)

    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        form = ProductFormImageView(
            request.POST or None, request.FILES or None, instance=prod)
        form1 = ProductIngredientFormset(request.POST or None)
        if form.is_valid() and form1.is_valid():
            ingrd.delete()
            form.save()
            for form in form1.forms:
                obj = ProductIngredients()
                obj.product = id
                obj.ingredient = form.cleaned_data.get('ingredient')
                obj.quantity = form.cleaned_data.get('quantity')
                obj.unit = form.cleaned_data.get('unit')
                obj.save()
            return redirect('wayrem_admin:productlist')
    form = ProductFormImageView(instance=prod)
    form1 = ProductIngredientFormset(queryset=ingrd)
    return render(request, 'product_update_latest.html', {'form': form, 'formset': form1, 'image': prod.primary_image, 'id': prod.id})


class DeleteProduct(View):
    @method_decorator(role_required('Products Delete'))
    def post(self, request):
        productid = request.POST.get('product_id')
        products = Products.objects.get(id=productid)
        products.delete()
        return redirect('wayrem_admin:productlist')


def view_product_suppliers(request):
    product = request.GET.get('product')
    po = SupplierProducts.objects.filter(SKU=product).order_by('price')
    return render(request, 'product_supplier.html', {"list": po})


def lowest_price_supplier(request):
    product = request.GET.get('product')
    po = SupplierProducts.objects.filter(SKU=product).order_by('price').first()
    return render(request, 'lowest_price.html', {"i": po})


def lowest_deliverytime_supplier(request):
    product = request.GET.get('product')
    po = SupplierProducts.objects.filter(
        SKU=product).order_by('deliverable_days').first()
    return render(request, 'lowest_price.html', {"i": po})


@role_required('Products View')
def product_details(request, id=None):
    prod = Products.objects.get(id=id)
    ingrd = ProductIngredients.objects.filter(product=id).all()
    form1 = ProductIngredientFormsetView(queryset=ingrd)
    form = ProductFormView(instance=prod)
    # prod = Products.objects.filter(id=id).first()
    return render(request, 'View_product copy.html', {'form': form, 'form2': form1, 'image': prod.primary_image, 'id': prod.id})
