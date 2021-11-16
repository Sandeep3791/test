from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import Products
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from wayrem_admin.services import *
from wayrem_admin.export import generate_excel, generate_pdf
from wayrem_admin.forms import ProductUpdateForm, ProductFormOne, ProductFormTwo, ProductFormThree, ProductFormFour


def product_excel(request):
    return generate_excel("product_master", "products")


def pdf_product(request):
    query = 'SELECT  SKU, product_code, product_meta_key, feature_product, product_deliverable, date_of_mfg, date_of_exp, mfr_name, dis_abs_percent, image1, image2, image3, image4, image5, product_name, description, ingredients1_id, ingredients2_id, ingredients3_id, ingredients4_id, calories1, calories2, calories3, calories4, nutrition, product_qty, product_weight, unit, price, discount, package_count, wayrem_margin, wayrem_abs_percent FROM product_master'
    template = "pdf_product.html"
    file = "products.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


def inputBar(request):
    if request.method == "POST":
        delSession(request)
        user_code = request.POST.get('code')
        data = barcodeDetail(user_code)
# data['products'][0]['barcode_number']
        try:
            request.session['SKU'] = data['products'][0]['barcode_number']
            request.session['product_name'] = data['products'][0]['title']
            request.session['description'] = data['products'][0]['description']
            request.session['model'] = data['products'][0]['model']
            request.session['product_meta_key'] = data['products'][0]['features']
            request.session['weight'] = data['products'][0]['weight']
            request.session['mfr_name'] = data['products'][0]['manufacturer']
            # request.session['product_code'] = data['products'][0]['asin']
            request.session['price'] = data['products'][0]['price']
        except:
            pass
        return redirect('wayrem_admin:productviewone')
    return render(request, 'inputBar.html')


def product(request):
    delSession(request)
    # messages.success(request, "Lorem ipsum")
    return render(request, 'preproduct.html')


def load_supplier(request):
    x = dict(request.GET)
    category = x.get('category_product[]')

    supplier = [Supplier.objects.filter(
        category_name=i).all() for i in category]
    # supplier = Supplier.objects.filter(category_name=category).all()
    return render(request, 'supplier_dropdown.html', {'supplier': supplier})


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
        'product_deliverable': request.session.get('product_deliverable', None),
        'date_of_mfg': request.session.get('date_of_mfg', None),
        'date_of_exp': request.session.get('date_of_exp', None),
        'mfr_name': request.session.get('mfr_name', None),
        'supplier_name': request.session.get('supplier_name', None),
    }
    context = {}
    form = ProductFormOne(request.POST, initial=initial)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            request.session['SKU'] = form.cleaned_data['SKU']
            request.session['product_category'] = form.cleaned_data['product_category']
            request.session['product_code'] = form.cleaned_data['product_code']
            request.session['product_name'] = form.cleaned_data['product_name']
            request.session['feature_product'] = form.cleaned_data['feature_product']
            request.session['product_deliverable'] = form.cleaned_data['product_deliverable']
            request.session['date_of_mfg'] = str(
                form.cleaned_data['date_of_mfg'])
            request.session['date_of_exp'] = str(
                form.cleaned_data['date_of_exp'])
            # json.dumps(doe, indent=4, sort_keys=True, default=str)
            request.session['mfr_name'] = form.cleaned_data['mfr_name']
            request.session['supplier_name'] = form.cleaned_data['supplier_name']

            # return HttpResponseRedirect(reverse('product-view-two'))
            return redirect('wayrem_admin:productviewtwo')
            # return HttpResponse(render(request,'path_to_your_view.html'))
    else:
        context['form'] = ProductFormOne(initial=initial)
    return render(request, 'product1.html', context)

# # ----------------------------------------------------------------------------


@ login_required(login_url='wayrem_admin:root')
def product_view_two(request):
    initial = {
        'product_weight': request.session.get('product_weight', None),
        'unit': request.session.get('unit', None),
        'price': request.session.get('price', None),
        'discount': request.session.get('discount', None),
        'dis_abs_percent': request.session.get('dis_abs_percent', None),
        'wayrem_margin': request.session.get('wayrem_margin', None),
        'wayrem_abs_percent': request.session.get('wayrem_abs_percent', None),
        'package_count': request.session.get('package_count', None),
        'product_meta_key': request.session.get('product_meta_key', None),
    }

    context = {}
    form = ProductFormTwo(request.POST, initial=initial)
    context['form'] = form
    # form = ProductFormTwo(request.POST or None, initial=initial)
    if request.method == 'POST':
        print("post")
        if form.is_valid():
            print("valid")
            request.session['product_weight'] = float(
                form.cleaned_data['product_weight'])
            request.session['unit'] = form.cleaned_data['unit']
            price = form.cleaned_data['price']
            request.session['price'] = float(price)
            request.session['discount'] = float(form.cleaned_data['discount'])
            request.session['dis_abs_percent'] = form.cleaned_data['dis_abs_percent']
            request.session['wayrem_margin'] = form.cleaned_data['wayrem_margin']
            request.session['wayrem_abs_percent'] = form.cleaned_data['wayrem_abs_percent']
            request.session['package_count'] = float(
                form.cleaned_data['package_count'])
            request.session['product_meta_key'] = form.cleaned_data['product_meta_key']
            return redirect('wayrem_admin:productviewthree')
    else:
        context['form'] = ProductFormTwo(initial=initial)
    return render(request, 'product2.html', context)

# ----------------------------------------------------------------------------------
# @login_required(login_url='/')


def product_view_three(request):
    initial = {
        # 'product_name': request.session.get('product_name', None),
        'description': request.session.get('description', None),
        'calories1': request.session.get('calories1', None),
        'calories2': request.session.get('calories2', None),
        'calories3': request.session.get('calories3', None),
        'calories4': request.session.get('calories4', None),
        'ingredients1': request.session.get('ingredients1', None),
        'ingredients2': request.session.get('ingredients2', None),
        'ingredients3': request.session.get('ingredients3', None),
        'ingredients4': request.session.get('ingredients4', None),
        'product_qty':  request.session.get('product_qty', None),
    }
    context = {}
    form = ProductFormThree(request.POST, initial=initial)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            request.session['description'] = form.cleaned_data['description']
            calories1 = form.cleaned_data['calories1']
            calories2 = form.cleaned_data['calories2']
            calories3 = form.cleaned_data['calories3']
            calories4 = form.cleaned_data['calories4']
            request.session['calories1'] = str(calories1)
            request.session['calories2'] = str(calories2)
            # request.session['calories2'] = json.dumps(
            # calories2, cls=DecimalEncoder)
            request.session['calories3'] = str(calories3)
            request.session['calories4'] = str(calories4)
            request.session['ingredients1'] = form.cleaned_data['ingredients1']
            request.session['ingredients2'] = form.cleaned_data['ingredients2']
            request.session['ingredients3'] = form.cleaned_data['ingredients3']
            request.session['ingredients4'] = form.cleaned_data['ingredients4']
            request.session['product_qty'] = form.cleaned_data['product_qty']
            # return HttpResponseRedirect(reverse('product_view_two'))
            return redirect('wayrem_admin:productviewfour')
    else:
        context['form'] = ProductFormThree(initial=initial)
    return render(request, 'product3.html', context)


def product_view_four(request):
    # initial = {
    #     'wayrem_margin': request.session.get('wayrem_margin', None),
    #     'wayrem_abs_percent': request.session.get('wayrem_abs_percent', None),
    # }
    context = {}
    form = ProductFormFour(request.POST, request.FILES)
    context['form'] = form
    if request.method == 'POST':
        print("Post")
        if form.is_valid():
            print("Valid Form")
            sku = request.session['SKU']
            product_code = request.session['product_code']
            product_meta_key = request.session['product_meta_key']
            feature_product = request.session['feature_product']
            product_deliverable = request.session['product_deliverable']
            mfr_name = request.session['mfr_name']
            date_of_mfg = request.session['date_of_mfg']
            date_of_exp = request.session['date_of_exp']
            product_name = request.session['product_name']
            description = request.session['description']
            calories1 = request.session['calories1']
            calories2 = request.session['calories2']
            calories3 = request.session['calories3']
            calories4 = request.session['calories4']
            product_qty = request.session['product_qty']
            product_weight = request.session['product_weight']
            unit = request.session['unit']
            price = request.session['price']
            discount = request.session['discount']
            wayrem_margin = request.session['wayrem_margin']
            wayrem_abs_percent = request.session['wayrem_abs_percent']
            package_count = request.session['package_count']
            ingredients1 = inst_Ingridient(request.session['ingredients1'])
            ingredients2 = inst_Ingridient(request.session['ingredients2'])
            ingredients3 = inst_Ingridient(request.session['ingredients3'])
            ingredients4 = inst_Ingridient(request.session['ingredients4'])
            category = [inst_Category(i)
                        for i in request.session['product_category']]
            supplier = [inst_Supplier(i)
                        for i in request.session['supplier_name']]
            # c
            image1 = form.cleaned_data['image1']
            image2 = form.cleaned_data['image2']
            image3 = form.cleaned_data['image3']
            image4 = form.cleaned_data['image4']
            image5 = form.cleaned_data['image5']

            prod = Products(SKU=sku, product_code=product_code, product_meta_key=product_meta_key, feature_product=feature_product, product_deliverable=product_deliverable, date_of_mfg=date_of_mfg, date_of_exp=date_of_exp,
                            mfr_name=mfr_name, product_name=product_name, description=description,
                            calories1=calories1, calories2=calories2, calories3=calories3, calories4=calories4, ingredients1=ingredients1,
                            ingredients2=ingredients2, ingredients3=ingredients3, ingredients4=ingredients4, product_qty=product_qty, product_weight=product_weight,
                            unit=unit, price=price, discount=discount, package_count=package_count, wayrem_margin=wayrem_margin, image1=image1, image2=image2, image3=image3, image4=image4, image5=image5, wayrem_abs_percent=wayrem_abs_percent)
            prod.save()
            prod.product_category.set(category)
            prod.supplier_name.set(supplier)
            prod.save()
            try:
                del request.session['ean']
                del request.session['title']
                del request.session['description']
                del request.session['model']
            except:
                pass
            messages.success(request, "Product created successfully!")
            return redirect('wayrem_admin:productlist')
    else:
        context['form'] = ProductFormFour()
    return render(request, 'product4.html', context)


class ProductList(View):
    template_name = "productlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        productslist = Products.objects.all()
        return render(request, self.template_name, {"productslist": productslist})


def product_details(request, id=None):
    prod = Products.objects.filter(id=id).first()
    return render(request, 'View_product.html', {'proddata': prod})


def update_product(request, id=None, *args, **kwargs):
    # print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        prod = Products.objects.get(id=id)
        form = ProductUpdateForm(request.POST or None,
                                 request.FILES or None, instance=prod)
        if form.is_valid():
            print("FORM")

            form.save()
            return redirect('wayrem_admin:productlist')
    prod = Products.objects.get(id=id)
    form = ProductUpdateForm(instance=prod)
    return render(request, 'UpdateProduct.html', {'form': form, 'id': prod.id})


class DeleteProduct(View):
    def post(self, request):
        productid = request.POST.get('product_id')
        products = Products.objects.get(id=productid)
        products.delete()
        return redirect('wayrem_admin:productlist')


def view_product_suppliers(request):
    product = request.GET.get('product')
    po = SupplierProducts.objects.filter(SKU=product).order_by('price')
    return render(request, 'product_supplier.html', {"list": po})
