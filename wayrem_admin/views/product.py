from wayrem.celery import app
from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
from django.db import connection
from django.http import response
from httplib2 import Response
from wayrem_admin.import_prod_img import *
from django.core.files.storage import default_storage
from sqlalchemy import create_engine
import pandas as pd
from pymysql import connect
from wayrem.settings import DATABASES
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.product_filters import ProductFilter
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.db.models import Q
import json
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.forms import supplier
from wayrem_admin.models import Products
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from wayrem_admin.services import *
from wayrem_admin.export import generate_excel
from wayrem_admin.forms import *
import biip
from django.forms import formset_factory
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required
from io import BytesIO


def product_excel(request):
    con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                  host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
    df = pd.DataFrame()
    df_pm = pd.read_sql(
        f'select * from products_master where is_deleted=False', con)
    df_um = pd.read_sql(f'select * from unit_master', con)
    df_pmc = pd.read_sql(f'select * from products_master_category', con)
    cc = pd.read_sql(
        f'select id,name from categories_master where is_parent = True', con)
    pc = pd.read_sql(
        f'select id,name from categories_master where is_parent = False', con)
    df_pmc_pc = pd.merge(df_pmc, pc, left_on="categories_id", right_on="id")
    df_pmc_cc = pd.merge(df_pmc, cc, left_on="categories_id", right_on="id")
    df_pmc_pc = df_pmc_pc.drop(['id_x', 'id_y'], axis=1)
    df_pmc_cc = df_pmc_cc.drop(['id_x', 'id_y'], axis=1)
    df_pmc_pc = df_pmc_pc.groupby('products_id', sort=False).name.apply(
        ', '.join).reset_index(name='categories')
    df_pmc_cc = df_pmc_cc.groupby('products_id', sort=False).name.apply(
        ', '.join).reset_index(name='subcategories')
    df_pmc = pd.merge(df_pmc_pc, df_pmc_cc, left_on='products_id',
                      right_on='products_id', indicator=True, how="outer")
    df_pmc = df_pmc.drop_duplicates(
        subset="products_id", keep='first', inplace=False)
    df_pc = pd.merge(df_pm, df_pmc, left_on='id', right_on='products_id')
    del df_pc['_merge']

    df_sm = pd.read_sql(f'select * from supplier_master', con)
    df_pms = pd.read_sql(f'select * from products_master_supplier', con)
    df_psm = pd.merge(df_pms, df_sm, left_on='supplier_id', right_on='id')
    df_psm = df_psm[['products_id', 'company_name']]
    df_psm = df_psm.groupby('products_id', sort=False).company_name.apply(
        ', '.join).reset_index(name='supplier')
    df_pc = pd.merge(df_pc, df_psm, indicator=True,
                     left_on='id', right_on='products_id', how="outer")
    df_pc = df_pc.drop(df_pc[df_pc._merge == "right_only"].index)
    del df_pc['_merge']
    df_pc = pd.merge(
        df_pc, df_um, indicator=True, left_on='weight_unit_id', right_on='id', how="outer")
    df_pc = df_pc.drop(
        df_pc[df_pc._merge == "right_only"].index)
    del df_pc['_merge']
    df_pc.rename(columns={'unit_name': 'weight_unit'}, inplace=True)
    df_pc = pd.merge(
        df_pc, df_um, indicator=True, left_on='quantity_unit_id', right_on='id', how="outer")
    df_pc = df_pc.drop(
        df_pc[df_pc._merge == "right_only"].index)
    del df_pc['_merge']
    df_pc.rename(columns={'unit_name': 'quantity_unit'}, inplace=True)
    df_pc['feature_product'] = df_pc['feature_product'].astype(bool)
    df_pc['publish'] = df_pc['publish'].astype(bool)
    df_pc['package_count'] = df_pc['package_count'].replace(
        {'True': True, 'False': False})
    excel_cols = {
        'sku': df_pc['SKU'],
        'name': df_pc['name'],
        'categories': df_pc['categories'],
        'sub-categories': df_pc['subcategories'],
        'manufacturer  name': df_pc['mfr_name'],
        'size': df_pc['weight'],
        'size unit': df_pc['weight_unit'],
        'available stock': df_pc['quantity'],
        'stock unit': df_pc['quantity_unit'],
        'starting inventory': df_pc['inventory_starting'],
        'shipped inventory': df_pc['inventory_shipped'],
        'received inventory': df_pc['inventory_received'],
        'removed inventory': df_pc['inventory_removed'],
        'cancelled inventory': df_pc['inventory_cancelled'],
        'date of manufacture': df_pc['date_of_mfg'],
        'date of expiry': df_pc['date_of_exp'],
        'price (in SAR)': df_pc['price'],
        'discount': df_pc['discount'],
        'discount unit': df_pc['dis_abs_percent'],
        'margin': df_pc['wayrem_margin'],
        'margin unit': df_pc['margin_unit'],
        'meta key': df_pc['meta_key'],
        'description': df_pc['description'],
        'outOfStock threshold': df_pc['outofstock_threshold'],
        'featured product': df_pc['feature_product'],
        'publish': df_pc['publish'],
        'package': df_pc['package_count'],
        'barcode': df_pc['barcode'],
        'supplier': df_pc['supplier'],
    }
    df = df.assign(**excel_cols)
    print(df)
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        # Set up the Http response.
        filename = 'products.xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


@permission_required('product_management.create_product_list', raise_exception=True)
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


class ProductCreate(LoginPermissionCheckMixin, View):
    permission_required = 'product_management.create_product_list'
    template_name = "inputBar.html"

    def get(self, request):
        delSession(request)
        return render(request, self.template_name)

    def post(self, request):
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


def details_gs1(request):
    delSession(request)
    user_code = request.GET.get('barcode')
    user_code = user_code.replace('\\x1d', '\x1d')
    try:
        result = biip.parse(user_code)
        request.session['gs1'] = user_code
        request.session['SKU'] = str(result.value)
        for item in result.gs1_message.element_strings:
            ai = item.ai.ai
            try:
                obj = GS1ProductFields.objects.get(ai_code=ai)
                if obj.product_field == "weight":
                    request.session['weight'] = str(item.decimal)
                    request.session['weight_unit'] = "kg"
                if obj.product_field == "price":
                    request.session['price'] = str(item.decimal)
                if obj.product_field == "date_of_exp":
                    request.session['date_of_exp'] = str(item.date)
                if obj.product_field == "date_of_mfg":
                    request.session['date_of_mfg'] = str(item.date)
            except:
                pass
        # request.session['SKU'] = result.gs1_message.element_strings[0].value
        # request.session['price'] = str(
        #     result.gs1_message.element_strings[5].decimal)
        # request.session['date_of_exp'] = str(
        #     result.gs1_message.element_strings[1].date)
        # request.session['weight'] = str(
        #     result.gs1_message.element_strings[4].decimal)
        # request.session['weight_unit'] = "kg"
    except:
        pass
    data = [request.session.get('SKU'), request.session.get(
        'price'), request.session.get('date_of_exp'), request.session.get('weight'), request.session.get('weight_unit'), request.session.get('date_of_mfg')]
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


@permission_required('product_management.create_product_list', raise_exception=True)
def product_view_one(request):
    initial = {
        'barcode': request.session.get("gs1", None),
        'name': request.session.get("name", None),
        'category': request.session.get("category", None),
        'meta_key': request.session.get("meta_key", None),
        'feature_product': request.session.get("feature_product", None),
        'publish': request.session.get("publish", None),
        'date_of_mfg': request.session.get("date_of_mfg", None),
        'date_of_exp': request.session.get("date_of_exp", None),
        'mfr_name': request.session.get("mfr_name", None),
        'supplier': request.session.get("supplier", None),
        'dis_abs_percent': request.session.get("dis_abs_percent", None),
        'description': request.session.get("description", None),
        'warehouse': request.session.get("warehouse", None),
        'quantity': request.session.get("quantity", None),
        'weight': request.session.get("weight", None),
        'weight_unit': request.session.get("weight_unit", None),
        'quantity_unit': request.session.get("weight_unit", None),
        'price': request.session.get("price", None),
        'discount': request.session.get("discount", None),
        'package_count': request.session.get("package_count", None),
        'wayrem_margin': request.session.get("wayrem_margin", None),
        'margin_unit': request.session.get("margin_unit", None),
        'outofstock_threshold': request.session.get("outofstock_threshold", None),
    }
    context = {}
    # form = ProductForm(request.POST, initial=initial)
    form = ProductFormOne(request.POST, initial=initial)
    formset = ProductIngredientFormset(request.POST)
    context['form'] = form
    context['formset'] = formset
    if request.method == 'POST':
        print("Post")
        print(formset.is_valid())
        print(formset.errors)
        print(form.is_valid())
        if form.is_valid() and formset.is_valid():
            # product = form.save()
            request.session["SKU"] = form.cleaned_data.get("SKU")
            request.session["barcode"] = form.cleaned_data.get("barcode")
            request.session["name"] = form.cleaned_data.get("name")
            request.session["category"] = form.cleaned_data.get("category")
            request.session["meta_key"] = form.cleaned_data.get("meta_key")
            request.session["feature_product"] = form.cleaned_data.get(
                "feature_product")
            request.session["publish"] = form.cleaned_data.get("publish")
            request.session["date_of_mfg"] = str(form.cleaned_data.get(
                "date_of_mfg"))
            request.session["date_of_exp"] = str(form.cleaned_data.get(
                "date_of_exp"))
            request.session["mfr_name"] = form.cleaned_data.get("mfr_name")
            request.session["supplier"] = form.cleaned_data.get("supplier")
            request.session["dis_abs_percent"] = form.cleaned_data.get(
                "dis_abs_percent")
            request.session["description"] = form.cleaned_data.get(
                "description")
            request.session["warehouse"] = form.cleaned_data.get("warehouse")
            request.session["quantity"] = form.cleaned_data.get("quantity")
            request.session["quantity_unit"] = form.cleaned_data.get(
                "weight_unit")
            request.session["weight"] = form.cleaned_data.get("weight")
            request.session["weight_unit"] = form.cleaned_data.get(
                "weight_unit")
            request.session["price"] = form.cleaned_data.get("price")
            request.session["discount"] = form.cleaned_data.get("discount")
            request.session["package_count"] = form.cleaned_data.get(
                "package_count")
            request.session["wayrem_margin"] = form.cleaned_data.get(
                "wayrem_margin")
            request.session["margin_unit"] = form.cleaned_data.get(
                "margin_unit")
            request.session["outofstock_threshold"] = form.cleaned_data.get(
                "outofstock_threshold")

            try:
                product_id = Products.objects.last().id
            except:
                product_id = 0
            product_id = product_id + 1
            exist = ProductIngredients.objects.filter(product=product_id).all()
            if exist:
                exist.delete()
            for form in formset.forms:
                obj = ProductIngredients()
                obj.product = product_id
                obj.ingredient = form.cleaned_data.get('ingredient')
                obj.quantity = form.cleaned_data.get('quantity')
                obj.unit = form.cleaned_data.get('unit')
                obj.save()
            request.session['product_pk'] = product_id
            return redirect('wayrem_admin:product_images')
            # return HttpResponse(render(request,'path_to_your_view.html'))
    else:
        context['form'] = ProductFormOne(initial=initial)
        context['formset'] = ProductIngredientFormset()
    return render(request, 'product/product1.html', context)


@permission_required('product_management.create_product_list', raise_exception=True)
def product_images(request):
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            primary_image = request.FILES.get('primary_image', None)
            featured_image = request.FILES.get('featured_image', None)
            category = [inst_Category(i)
                        for i in request.session["category"]]
            supplier = [inst_Supplier(i)
                        for i in request.session["supplier"]]
            obj = Products()
            obj.id = request.session.get('product_pk')
            obj.SKU = request.session.get("SKU", None)
            if len(request.session.get("barcode", None)) > 0:
                obj.barcode = request.session.get("barcode", None)
            obj.name = request.session.get("name", None)
            obj.meta_key = request.session.get("meta_key", None)
            obj.feature_product = request.session.get("feature_product", None)
            obj.publish = request.session.get("publish", None)
            dom = request.session.get("date_of_mfg", None)
            doe = request.session.get("date_of_exp", None)
            if dom == "None":
                dom = None
            if doe == "None":
                doe = None
            obj.date_of_mfg = dom
            obj.date_of_exp = doe
            obj.mfr_name = request.session.get("mfr_name", None)
            obj.dis_abs_percent = request.session.get("dis_abs_percent", None)
            obj.description = request.session.get("description", None)
            obj.quantity = request.session.get("quantity", None)
            obj.quantity_unit = inst_Unit(
                request.session.get("weight_unit", None))
            obj.weight = request.session.get("weight", None)
            obj.weight_unit = inst_Unit(
                request.session.get("weight_unit", None))
            obj.price = request.session.get("price", None)
            obj.discount = request.session.get("discount", None)
            obj.package_count = request.session.get("package_count", None)
            obj.wayrem_margin = request.session.get("wayrem_margin", None)
            obj.margin_unit = request.session.get("margin_unit", None)
            obj.warehouse = inst_Warehouse(
                request.session.get("warehouse", None))
            obj.primary_image = primary_image
            obj.featured_image = featured_image
            obj.save()
            obj.category.set(category)
            obj.supplier.set(supplier)
            inventory_dict = {'inventory_type_id': 1, 'quantity': request.session.get("quantity", None), 'product_id': obj.id, 'warehouse_id': request.session.get(
                "warehouse", None), 'po_id': None, 'supplier_id': None, 'order_id': None, 'order_status': None}
            Inventory().insert_inventory(inventory_dict)
            images = request.FILES.getlist('images')
            for image in images:
                img_obj = Images()
                img_obj.image = image
                img_obj.product = obj
                img_obj.save()
            return redirect('wayrem_admin:productlist')

    else:
        form = ProductImageForm()
    return render(request, "product/product2.html", {'form': form})


# # ----------------------------------------------------------------------------


class ProductList(LoginPermissionCheckMixin, ListView):
    permission_required = 'product_management.manage_product_list'
    model = Products
    template_name = "product/list.html"
    context_object_name = 'productslist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:productlist')

    def get_queryset(self):
        qs = Products.objects.filter(is_deleted=False)
        filtered_list = ProductFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        delSession(self.request)
        context = super(ProductList, self).get_context_data(**kwargs)
        context['filter_form'] = ProductAdvanceFilterForm(self.request.GET)
        return context


@permission_required('product.view', raise_exception=True)
def product_details(request, id=None):
    prod = Products.objects.get(id=id)
    ingrd = ProductIngredients.objects.filter(product=id).all()
    prodimage = Images.objects.filter(product_id=id).all()
    form1 = ProductIngredientFormsetView(queryset=ingrd)
    print(form1)
    form = ProductFormView(instance=prod)
    # prod = Products.objects.filter(id=id).first()
    return render(request, 'product/view_product.html', {'form': form, 'form2': form1, 'primary_image': prod.primary_image, 'featured_image': prod.featured_image, 'prodimg': prodimage, 'id': prod.id})


@permission_required('product.edit', raise_exception=True)
def update_product(request, id=None, *args, **kwargs):
    # print(id)

    ingrd = ProductIngredients.objects.filter(product=id).all()
    prod = Products.objects.get(id=id)
    product_images = Images.objects.filter(product=id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        form = ProductFormImageView(
            request.POST or None, request.FILES or None, instance=prod)
        form1 = ProductIngredientFormset1(request.POST or None)
        form3 = ProductImgUpdateForm(request.POST, request.FILES)
        # form2 = ProductImageFormset(
        # request.POST or None, request.FILES or None)
        if form.is_valid() and form1.is_valid() and form3.is_valid():
            ingrd.delete()
            prod = form.save()
            prod.quantity_unit = prod.weight_unit
            prod.save()
            for form in form1.forms:
                obj = ProductIngredients()
                obj.product = id
                obj.ingredient = form.cleaned_data.get('ingredient')
                obj.quantity = form.cleaned_data.get('quantity')
                obj.unit = form.cleaned_data.get('unit')
                obj.save()
            images = request.FILES.getlist('images')
            for image in images:
                img_obj = Images()
                img_obj.image = image
                img_obj.product_id = id
                img_obj.save()
            return redirect('wayrem_admin:productlist')
    else:
        form = ProductFormImageView(instance=prod)
        form1 = ProductIngredientFormset1(queryset=ingrd)
        # form2 = ProductImageFormset(queryset=product_images)
        form3 = ProductImgUpdateForm()
    context = {'form': form, 'formset': form1, 'form3': form3, 'primary_image': prod.primary_image,
               'featured_image': prod.featured_image, 'product_images': product_images, 'id': prod.id}
    return render(request, 'product/product_update.html', context)


class DeleteProduct(LoginPermissionCheckMixin, View):
    permission_required = 'product.delete'

    def post(self, request):
        productid = request.POST.get('product_id')
        products = Products.objects.get(id=productid)
        products.SKU = products.SKU + " (not available)"
        products.is_deleted = True
        products.publish = False
        products.save()
        messages.success(request, "Product Deleted Successfully!")
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


def update_product_images(request):
    if request.method == "POST":
        image = request.FILES.get('updateimage')
        product_id = request.POST.get('updateimageID')
        obj = Images.objects.get(id=product_id)
        obj.image = image
        obj.save()
        return HttpResponse("Image updated Successfully!!")
    return HttpResponse("Please provide Image!")


def delete_product_images(request):
    product_id = request.GET.get('deleteimage')
    obj = Images.objects.get(id=product_id)
    obj.delete()
    return HttpResponse("Image Delete Successfully!!")


@permission_required('product_management.import_product_list', raise_exception=True)
def import_excel(request):
    if request.method == "POST":
        delSession(request)
        file = request.FILES["myFileInput"]
        required_cols = ['sku*', 'product name*', 'manufacture date', 'expiry date', 'manufacturer name', 'description', 'weight', 'weight unit', 'quantity',
                         'quantity unit', 'price', 'discount', 'discount unit', 'wayrem_margin', 'margin_unit', 'meta tags', 'feature_product', 'publish', 'package_count', 'category']
        df = pd.read_excel(file)
        excel_cols = list(df.columns)
        missing_cols = list(set(required_cols) - set(excel_cols))
        unwanted_cols = list(set(excel_cols) - set(required_cols))
        if len(excel_cols) == 20 and required_cols == excel_cols:
            duplicate_entries = len(df[df.duplicated('sku*')])
            total_entries = len(df)
            context = {
                "total_entries": total_entries,
                "duplicate_entries": duplicate_entries
            }
            file_name = default_storage.save(file.name, file)
            request.session['excel_product'] = file_name
            return render(request, "product/import_product.html", context)
        else:
            context = {
                "missing_columns": missing_cols,
                "unwanted_columns": unwanted_cols
            }
            return render(request, "product/import_product.html", context)
    delSession(request)
    return render(request, 'product/import_product.html')


def import_products(request):
    try:
        file_name = request.session.get('excel_product', None)
        if file_name is None:
            messages.error(request, "File is missing. Upload Again!")
            return redirect('wayrem_admin:import_excel')
        last_id = Products.objects.last()
        if last_id:
            last_id = last_id.id
        else:
            last_id = 0
        # file = request.FILES["myFileInput"]
        file = default_storage.open(file_name)
        df = pd.read_excel(file)
        total_excel_records = len(df)
        engine = create_engine(
            f"mysql+pymysql://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}/{DATABASES['default']['NAME']}?charset=utf8")
        con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                      host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
        df_products = pd.read_sql(
            'select * from products_master', con)
        df_products['SKU'] = df_products['SKU'].astype(str)
        df_category = pd.read_sql('select * from categories_master', con)
        df['category'] = df['category'].fillna('None')
        df_category["name"] = df_category["name"].str.lower()
        df["category"] = df["category"].str.lower()
        df_units = pd.read_sql('select * from unit_master', con)
        del df_units['is_active']
        duplicate_excel_records = len(df[df.duplicated('sku*')])
        df = df.drop_duplicates(subset="sku*", keep='first', inplace=False)
        # NaN values removed from sku and product name
        df = df[df['sku*'].notna()]
        df = df[df['product name*'].notna()]
        # df["first_column"] = df["first_column"].str.lower()
        dict = {'sku*': 'SKU',
                'product name*': 'name',
                'manufacturer name': 'mfr_name',
                'manufacture date': 'date_of_mfg',
                'expiry date': 'date_of_exp',
                'weight unit': 'weight_unit',
                'weight': 'weight',
                'quantity unit': 'quantity_unit',
                'quantity': 'quantity',
                'price': 'price',
                'discount unit': 'dis_abs_percent',
                'wayrem margin': 'wayrem_margin',
                'margin unit': 'margin_unit',
                'meta tags': 'meta_key',
                'feature product': 'feature_product',
                'package count': 'package_count',
                }
        df.rename(columns=dict, inplace=True)
        df['price'] = df['price'].fillna(0)
        df['weight'] = df['weight'].fillna(0)
        df['quantity'] = df['quantity'].fillna(0)
        df['discount'] = df['discount'].fillna(0)
        df['wayrem_margin'] = df['wayrem_margin'].fillna(0)
        df['price'] = df['price'].astype(float)
        df['weight'] = df['weight'].astype(float)
        df['quantity'] = df['quantity'].astype(float)
        df['discount'] = df['discount'].astype(float)
        df['wayrem_margin'] = df['wayrem_margin'].astype(float)
        df['weight_unit'] = df['weight_unit'].fillna("None")
        df['quantity_unit'] = df['quantity_unit'].fillna("None")
        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()
        df['warehouse_id'] = 1
        df['gs1'] = ""
        df['primary_image'] = ""
        df['featured_image'] = ""
        df['inventory_starting'] = df['quantity']
        df['inventory_shipped'] = 0
        df['inventory_cancelled'] = 0
        df['inventory_onhand'] = df['quantity']
        df['inventory_received'] = 0
        df['inventory_removed'] = 0
        df['outofstock_threshold'] = 0
        df['is_deleted'] = False
        try:
            weight_unit = pd.merge(
                df, df_units, left_on='weight_unit', right_on='unit_name')
            weight_unit_id = weight_unit['id']
        except:
            weight_unit_id = None
        try:
            quantity_unit = pd.merge(
                df, df_units, left_on='quantity_unit', right_on='unit_name')
            quantity_unit_id = quantity_unit['id']
        except:
            quantity_unit_id = None
        del df['weight_unit']
        del df['quantity_unit']
        df['weight_unit_id'] = weight_unit_id
        df['quantity_unit_id'] = quantity_unit_id
        df['SKU'] = df['SKU'].astype(str)
        df7 = df[~df.SKU.isin(df_products.SKU)]
        count_df = len(df7)
        ids = [i for i in range(last_id+1, last_id+count_df+1)]
        df7['id'] = ids
        categories_products = pd.DataFrame(
            df7.category.str.split(',').tolist(), index=df7.id).stack()
        categories_products = categories_products.reset_index()[[0, 'id']]
        categories_products.columns = ['categories', 'products_id']
        df_prod_cat = pd.merge(
            categories_products, df_category, left_on='categories', right_on='name')
        df_products_categories = pd.DataFrame()
        df_products_categories['products_id'] = df_prod_cat['products_id']
        df_products_categories['categories_id'] = df_prod_cat['id']
        del df7['category']
        inserted_records = len(df7)
        df7.to_sql('products_master', engine,
                   if_exists='append', index=False)
        df_products_categories.to_sql(
            'products_master_category', engine, if_exists='append', index=False)
        inventory_df = pd.DataFrame()
        inventory_df['quantity'] = df7['quantity']
        inventory_df['po_id'] = None
        inventory_df['supplier_id'] = None
        inventory_df['order_id'] = None
        inventory_df['order_status'] = None
        inventory_df['created_at'] = datetime.now()
        inventory_df['updated_at'] = datetime.now()
        inventory_df['inventory_type_id'] = 1
        inventory_df['product_id'] = ids
        inventory_df['warehouse_id'] = 1
        inventory_df = inventory_df[inventory_df.quantity != 0]
        inventory_df.to_sql('inventory', engine,
                            if_exists='append', index=False)
        ingredients = pd.DataFrame()
        ingredients['product'] = ids
        ingredients['quantity'] = 1
        ingredients['ingredient_id'] = None
        ingredients['unit_id'] = None
        ingredients.to_sql('product_ingredients', engine,
                           if_exists='append', index=False)
        default_storage.delete(file_name)
        delSession(request)
        context = {
            "total_excel_records": total_excel_records,
            "duplicate_excel_records": duplicate_excel_records,
            "inserted_records": inserted_records
        }
        if inserted_records == 0:
            messages.error(request, "Products already exists!")
        else:
            messages.success(request, "Products Imported Successfully!")
        return render(request, "product/import_results.html", context)
    except Exception as e:
        print(e)
        messages.error(request, "Please select a valid file!")
        return redirect('wayrem_admin:import_excel')


def import_result(request):
    messages.success(request, "Hello world!!!")
    return render(request, "product/import_results.html")


def check_import_status(request):
    # client_dir = '/home/suryaaa/Music/image_testing/client-images'
    # client_dir = '/opt/app/wayrem-admin-backend/media/wayrem-product-images'
    client_dir = os.path.join(os.path.abspath(
        "."), "media", "wayrem-product-images")
    sku_folders = [f for f in os.listdir(
        client_dir) if os.path.isdir(os.path.join(client_dir, f))]
    # failed_dir = f"/home/suryaaa/Music/image_testing/failed"
    # failed_dir = f"/opt/app/wayrem-admin-backend/media/common_folder/failed"
    failed_dir = os.path.join(os.path.abspath(
        "."), "media", "common_folder", "failed")
    failed_sku_folders = [f for f in os.listdir(
        failed_dir) if os.path.isdir(os.path.join(failed_dir, f))]
    img = Images.objects.values('product_id').distinct().count()
    prod = Products.objects.all().count()
    query = "SELECT * FROM   products_master WHERE  NOT EXISTS  (SELECT * FROM   product_images WHERE  product_images.product_id = products_master.id)"
    with connection.cursor() as cursor:
        no_image_sku = cursor.execute(query)
    context = {
        "available_folders": len(sku_folders),
        "failed_folders": len(failed_sku_folders),
        "no_image_products": no_image_sku,
        "total_product_images": prod,
        "product_with_imgs": img
    }
    response = HttpResponse(json.dumps(context))
    return response
    # return render(request, "product/img_status.html", context)


def import_single_image(request):
    # path = '/home/suryaaa/Music/image_testing/client-images'
    path = os.path.join(os.path.abspath(
        '.'), "media", "common_folder", "import_images")
    # path = '/opt/app/wayrem-admin-backend/media/wayrem-product-images'

    items = [f for f in os.listdir(
        path) if not os.path.isdir(os.path.join(path, f))]

    print(items)

    for file in items:
        file_name = file.split(".")[0].lower()
        product = Products.objects.filter(name__icontains=file_name).first()
        # product = Products.objects.filter(SKU=i).first()
        common_folder = os.path.join(
            os.path.abspath('.'), "media", "common_folder")
        if product:
            src_dir = os.path.join(path, file)
            # dst_dir = f"/home/suryaaa/Music/database/products/{i}/"
            # dst_dir = f"{common_folder}/products/{product.SKU}/"
            dst_dir = os.path.join(common_folder, "products", product.SKU)
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            if os.path.isfile(src_dir):
                destination = os.path.join(dst_dir, file.replace(' ', '_'))
                shutil.copy(src_dir, destination)
                product.primary_image = f"products/{product.SKU}/{file.replace(' ', '_')}"
                print("default image copied")
                product.save()
                extention = file.split('.')[-1]
                num = random.randint(111, 999)
                fname = '{}_{}.{}'.format(file_name, product.SKU, extention)
                destination = os.path.join(dst_dir, fname)
                shutil.copy(src_dir, destination)
                img = Images()
                img.product = product
                img.image = f"products/{product.SKU}/{fname}"
                img.save()
                print('copied', file_name)
            os.remove(src_dir)
        else:
            source = os.path.join(path, file)
            # dst_dir = f"/home/suryaaa/Music/image_testing/failed"
            dst_dir = os.path.join(common_folder, "failed")
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            destination = os.path.join(dst_dir, file)
            shutil.copy(source, destination)
            print('copied', file)
            os.remove(source)
            print("failed!!")
    print("done")
    return HttpResponse("Successfully imported!!")


def bulk_publish_excel(request):
    if request.method == "POST":
        file = request.FILES["myFileInput"]
        required_cols = ['sku', 'publish', 'product name', 'brand']
        df = pd.read_excel(file)
        excel_cols = list(df.columns)
        required_cols.sort()
        excel_cols.sort()
        missing_cols = list(set(required_cols) - set(excel_cols))
        unwanted_cols = list(set(excel_cols) - set(required_cols))
        if len(excel_cols) == 4 and required_cols == excel_cols:
            del df['product name']
            del df['brand']
            con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                          host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
            df_products = pd.read_sql(
                'select * from products_master', con)
            df.rename(columns={"sku": "SKU"}, inplace=True)
            df = df.drop_duplicates(subset="SKU", keep='first', inplace=False)
            # NaN values removed from sku and product name
            df = df[df['SKU'].notna()]
            df = df[df['publish'].notna()]
            df['SKU'] = df['SKU'].astype(str)
            df['publish'] = df['publish'].astype(bool)
            df_products['SKU'] = df_products['SKU'].astype(str)
            # df_updated = df_products[df_products.set_index(
            #     ['SKU']).index.isin(df.set_index(['SKU']).index)]
            df_updated = df[df.set_index(
                ['SKU']).index.isin(df_products.set_index(['SKU']).index)]
            unpublished = df_updated[df_updated['publish'] == False]
            published = df_updated[df_updated['publish'] == True]
            unpublished_list = """' , '""".join(
                [str(item) for item in unpublished['SKU'].tolist()])
            unpublished_list = "'" + \
                unpublished_list[:] + "'" + unpublished_list[0:0]
            published_list = """' , '""".join(
                [str(item) for item in published['SKU'].tolist()])
            published_list = "'" + \
                published_list[:] + "'" + published_list[0:0]
            unpublished_query = f"UPDATE products_master SET publish = False where SKU in ({unpublished_list})"
            published_query = f"UPDATE products_master SET publish = True where SKU in ({published_list})"
            # df_updated = pd.merge(
            #     df.reset_index(), df_products, how='inner').set_index('index')
            if len(unpublished_list) > 0:
                with connection.cursor() as cursor:
                    cursor.execute(unpublished_query)
            if len(published_list) > 0:
                with connection.cursor() as cursor:
                    cursor.execute(published_query)
            context = {
                "published": len(published['SKU'].tolist()),
                "unpublished": len(unpublished['SKU'].tolist())
            }
            return render(request, "product/import_product.html", context)
        else:
            context = {
                "missing_columns": missing_cols,
                "unwanted_columns": unwanted_cols
            }
            return render(request, "product/import_product.html", context)
    return render(request, 'product/import_product.html')


@app.task()
def update_price_bulk(sku_list, price_list):
    print(sku_list, price_list)
    for sku, price in zip(sku_list, price_list):
        try:
            product_price = Products.objects.get(SKU=sku)
            product_price.price = price
            product_price.save()
            print(sku, price, "successfull")
        except Exception as e:
            print(sku, price, "failed", e)
    print("Price Updation Done")
    return {"status": True}


def divide_chunks(l, n):
    #! divide chunks is for dividing the list into n equal parts
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def bulk_price_excel(request):
    if request.method == "POST":
        file = request.FILES["myFileInput"]
        required_cols = ['sku', 'price', 'product name', 'brand']
        df = pd.read_excel(file)
        excel_cols = list(df.columns)
        required_cols.sort()
        excel_cols.sort()
        missing_cols = list(set(required_cols) - set(excel_cols))
        unwanted_cols = list(set(excel_cols) - set(required_cols))
        if len(excel_cols) == 4 and required_cols == excel_cols:
            try:
                del df['product name']
                del df['brand']
                con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                              host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
                df_products = pd.read_sql(
                    'select * from products_master', con)
                df.rename(columns={"sku": "SKU"}, inplace=True)
                df = df.drop_duplicates(
                    subset="SKU", keep='first', inplace=False)
                # NaN values removed from sku and product name
                df = df[df['SKU'].notna()]
                df = df[df['price'].notna()]
                df['price'] = df['price'].astype(float)
                df_products['SKU'] = df_products['SKU'].astype(str)
                df['SKU'] = df['SKU'].astype(str)
                # df_updated = df_products[df_products.set_index(
                #     ['SKU']).index.isin(df.set_index(['SKU']).index)]
                df_updated = df[df.set_index(
                    ['SKU']).index.isin(df_products.set_index(['SKU']).index)]
                sku_s = df_updated['SKU'].tolist()
                prices = df_updated['price'].tolist()
                if len(sku_s) > 0:
                    sku_list = list(divide_chunks(sku_s, 25))
                    price_list = list(divide_chunks(prices, 25))
                    for sku, price in zip(sku_list, price_list):
                        print("working", sku, price)
                        update_price_bulk.delay(sku, price)
                context = {
                    "total_entries_excel": len(df),
                    "price_sku_count": len(sku_s)
                }
                return render(request, "product/import_product.html", context)
            except Exception as e:
                print(e)
                messages.success(request, "Wrong Excel format!")
                return render(request, "product/import_product.html")
        else:
            context = {
                "missing_columns": missing_cols,
                "unwanted_columns": unwanted_cols
            }
            return render(request, "product/import_product.html", context)
    return render(request, 'product/import_product.html')


@app.task()
def update_quantity_bulk(sku_list, quantity_list):
    print(sku_list, quantity_list)
    for sku, quantity in zip(sku_list, quantity_list):
        try:
            product = Products.objects.get(SKU=sku)
            inventory_dict = {'inventory_type_id': 1, 'quantity': quantity, 'product_id': product.id,
                              'warehouse_id': 1, 'po_id': None, 'supplier_id': None, 'order_id': None, 'order_status': None}
            Inventory().insert_inventory(inventory_dict)
            Inventory().update_product_quantity(product.id)
            print(sku, quantity, "successfull")
        except Exception as e:
            print(sku, quantity, "failed", e)
    print("Quantity Updation Done")
    return {"status": True}


@app.task()
def remove_quantity_bulk(sku_list, quantity_list):
    print(sku_list, quantity_list)
    for sku, quantity in zip(sku_list, quantity_list):
        try:
            product = Products.objects.get(SKU=sku)
            inventory_dict = {'inventory_type_id': 5, 'quantity': quantity, 'product_id': product.id,
                              'warehouse_id': 1, 'po_id': None, 'supplier_id': None, 'order_id': None, 'order_status': None}
            Inventory().insert_inventory(inventory_dict)
            Inventory().update_product_quantity(product.id)
            print(sku, quantity, "successfull")
        except Exception as e:
            print(sku, quantity, "failed", e)
    print("Quantity Updation Done")
    return {"status": True}


def bulk_quantity_excel(request):
    if request.method == "POST":
        file = request.FILES["myFileInput"]
        required_cols = ['sku', 'add quantity',
                         'remove quantity', 'product name', 'brand']
        df = pd.read_excel(file)
        excel_cols = list(df.columns)
        required_cols.sort()
        excel_cols.sort()
        missing_cols = list(set(required_cols) - set(excel_cols))
        unwanted_cols = list(set(excel_cols) - set(required_cols))
        if len(excel_cols) == 5 and required_cols == excel_cols:
            try:
                cols = ['add quantity', 'remove quantity']
                df[cols] = df[cols].apply(
                    pd.to_numeric, errors='coerce', axis=1)
                del df['product name']
                del df['brand']
                con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                              host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
                df_products = pd.read_sql(
                    'select * from products_master', con)
                df.rename(columns={"sku": "SKU", "add quantity": "add_quantity",
                          "remove quantity": "remove_quantity"}, inplace=True)
                # NaN values removed from sku and product name
                df_add = df[df[['SKU', 'add_quantity']].notna().all(1)]
                df_add = df_add.drop_duplicates(
                    subset="SKU", keep='first', inplace=False)
                df_remove = df[df[['SKU', 'remove_quantity']].notna().all(1)]
                df_remove = df_remove.drop_duplicates(
                    subset="SKU", keep='first', inplace=False)
                df_add = df_add[df_add.add_quantity > 0]
                df_remove = df_remove[df_remove.remove_quantity > 0]
                df_products['SKU'] = df_products['SKU'].astype(str)
                df_add['SKU'] = df_add['SKU'].astype(str)
                df_remove['SKU'] = df_remove['SKU'].astype(str)
                df_updated_add = df_add[df_add.set_index(
                    ['SKU']).index.isin(df_products.set_index(['SKU']).index)]
                df_updated_remove = df_remove[df_remove.set_index(
                    ['SKU']).index.isin(df_products.set_index(['SKU']).index)]
                sku_s_add = df_updated_add['SKU'].tolist()
                sku_s_remove = df_updated_remove['SKU'].tolist()
                quantitys_add = df_updated_add['add_quantity'].tolist()
                quantitys_remove = df_updated_remove['remove_quantity'].tolist(
                )
                if len(sku_s_add) > 0:
                    sku_list = list(divide_chunks(sku_s_add, 25))
                    quantity_list = list(divide_chunks(quantitys_add, 25))
                    for sku, quantity in zip(sku_list, quantity_list):
                        print("working", sku, quantity)
                        update_quantity_bulk.delay(sku, quantity)
                if len(sku_s_remove) > 0:
                    sku_list = list(divide_chunks(sku_s_remove, 25))
                    quantity_list = list(divide_chunks(quantitys_remove, 25))
                    for sku, quantity in zip(sku_list, quantity_list):
                        print("working", sku, quantity)
                        remove_quantity_bulk.delay(sku, quantity)
                context = {
                    "total_entries_excel": len(df),
                    "quantity_sku_count": len(sku_s_add),
                    "quantity_sku_count_remove": len(sku_s_add)
                }
                return render(request, "product/import_product.html", context)
            except Exception as e:
                print(e)
                messages.error(request, "Wrong Excel format!")
                return render(request, "product/import_product.html")
        else:
            context = {
                "missing_columns": missing_cols,
                "unwanted_columns": unwanted_cols
            }
            return render(request, "product/import_product.html", context)
    return render(request, 'product/import_product.html')


class BarcodeProduct(View):
    template_name = 'product/barcode_product.html'

    def get(self, request):
        return render(request, self.template_name)

    # def post(self, request):
    #     try:
    #         code = request.POST.get("barcode")
    #         product = Products.objects.filter(
    #             gs1=code, is_deleted=False).first()
    #         return render(request, "product/product_view_pop.html", {"product": product})
    #     except Exception as e:
    #         print(e)
    #         messages.error(request, "No match found!!")
    #         return redirect('wayrem_admin:product_barcode')


def scan_result(request):
    try:
        code = request.GET.get("barcode")
        product = Products.objects.filter(
            barcode=code, is_deleted=False).first()
        form = ProductFormView(instance=product)
        return render(request, "product/product_view_pop.html", {"form": form, "quantity_unit": product.quantity_unit, "supplier": product.supplier, "product": product})
    except Exception as e:
        print(e)
        return render(request, "product/product_view_pop.html", {"message": "Barcode is not available!!"})


def import_primary_image(request):
    # path = '/home/suryaaa/Music/image_testing/client-images'
    path = os.path.join(os.path.abspath(
        '.'), "media", "common_folder", "import_images")
    # path = '/opt/app/wayrem-admin-backend/media/wayrem-product-images'

    items = [f for f in os.listdir(
        path) if not os.path.isdir(os.path.join(path, f))]

    print(items)

    for file in items:
        file_name = file.split(".")[0].lower()
        product = Products.objects.filter(name__icontains=file_name).first()
        # product = Products.objects.filter(SKU=i).first()
        common_folder = os.path.join(
            os.path.abspath('.'), "media", "common_folder")
        if product:
            src_dir = os.path.join(path, file)
            # dst_dir = f"/home/suryaaa/Music/database/products/{i}/"
            # dst_dir = f"{common_folder}/products/{product.SKU}/"
            dst_dir = os.path.join(common_folder, "products", product.SKU)
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            if os.path.isfile(src_dir):
                destination = os.path.join(dst_dir, file.replace(' ', '_'))
                shutil.copy(src_dir, destination)
                product.primary_image = f"products/{product.SKU}/{file.replace(' ', '_')}"
                print("default image copied")
                product.save()
                print('copied', file_name)
            os.remove(src_dir)
        else:
            source = os.path.join(path, file)
            # dst_dir = f"/home/suryaaa/Music/image_testing/failed"
            dst_dir = os.path.join(common_folder, "failed")
            isExist = os.path.exists(dst_dir)
            if not isExist:
                os.makedirs(dst_dir)
            destination = os.path.join(dst_dir, file)
            shutil.copy(source, destination)
            print('copied', file)
            os.remove(source)
            print("failed!!")
    print("done")
    return HttpResponse("Successfully imported!!")
