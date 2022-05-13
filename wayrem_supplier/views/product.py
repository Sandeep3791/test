from django.shortcuts import render, redirect
from django.views import View
from wayrem_supplier.models import Categories, SupplierProducts, Products, BestProductsSupplier
from wayrem_supplier.forms import SupplierProductForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from wayrem_supplier.export import generate_excel
import constant
from django.db.models import Q


class SupplierProductList(View):
    template_name = "supplier_product_list.html"

    def get(self, request, format=None):
        if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
        supplier_id = request.session.get("supplier_id")
        prodtslist = SupplierProducts.objects.filter(
            supplier_id=supplier_id).all()
        paginator = Paginator(prodtslist, 25)
        page = request.GET.get('page')
        try:
            productslist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            productslist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            productslist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"productslist": productslist})


class WayremproductList(View):
    template_name = "wayrem_product_list.html"

    def get(self, request, format=None):
        if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
        supplierid = request.session['supplier_id']
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT SKU FROM {constant.database}.product_suppliers where supplier_id_id="{supplierid}";')
            a = cursor.fetchall()
            v = list(a)
            ab = [i[0] for i in v]
            y = tuple(ab)
            print(ab)
        try:
            if len(y) == 1:
                d = y[0]
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'SELECT * FROM {constant.database}.products_master where SKU != {d}')
                    prodlist = cursor.fetchall()
            else:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'SELECT * FROM {constant.database}.products_master where SKU NOT IN {y}')
                    prodlist = cursor.fetchall()

                    product_name = request.GET.get('product_name')
                    product_sku = request.GET.get('product_sku')
                    # product_category = request.GET.get('product_category')
                    if product_name:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f'SELECT * FROM {constant.database}.products_master where name = "{product_name}"')
                            prodlist = cursor.fetchall()
                    if product_sku:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                f'SELECT * FROM {constant.database}.products_master where SKU = "{product_sku}"')
                            prodlist = cursor.fetchall()
                    # if product_category:
                    #     with connection.cursor() as cursor:
                    #         cursor.execute(f'SELECT * FROM {constant.database}.products_master where category = "{product_category}"')
                    #         prodlist= cursor.fetchall()
            # cat = Categories.objects.values_list('name', flat=True)
            paginator = Paginator(prodlist, 25)
            page = request.GET.get('page')
            try:
                productslist = paginator.page(page)
            except PageNotAnInteger:
                productslist = paginator.page(1)
            except EmptyPage:
                productslist = paginator.page(paginator.num_pages)
            return render(request, self.template_name, {"productslist": productslist})

        except:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'SELECT * FROM {constant.database}.products_master')
                prodlist = cursor.fetchall()

                product_name = request.GET.get('product_name')
                product_sku = request.GET.get('product_sku')
                # product_category = request.GET.get('product_category')
                if product_name:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f'SELECT * FROM {constant.database}.products_master where name = "{product_name}"')
                        prodlist = cursor.fetchall()
                if product_sku:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f'SELECT * FROM {constant.database}.products_master where SKU = "{product_sku}"')
                        prodlist = cursor.fetchall()
                # if product_category:
                #     with connection.cursor() as cursor:
                #         cursor.execute(f'SELECT * FROM {constant.database}.products_master where category__name = "{product_category}"')
                #         prodlist= cursor.fetchall()
            # cat = Categories.objects.values_list('name', flat=True)
            paginator = Paginator(prodlist, 25)
            page = request.GET.get('page')
            try:
                productslist = paginator.page(page)
            except PageNotAnInteger:
                productslist = paginator.page(1)
            except EmptyPage:
                productslist = paginator.page(paginator.num_pages)
            return render(request, self.template_name, {"productslist": productslist})


def add_product(request, id=None, *args, **kwargs):
    if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
    pdname = Products.objects.filter(id=id).first()
    supplier_id = request.session.get("supplier_id")
    form = SupplierProductForm(
        initial={"product_name": pdname.name, "SKU": pdname.SKU, "supplier_id": supplier_id})
    return render(request, 'add_product.html', {'form': form, 'product_name': pdname.name, "SKU": pdname.SKU})


def add_product_save(request):

    if request.method == "POST":
        form = SupplierProductForm(request.POST or None)
        if form.is_valid():
            SKU = form.cleaned_data['SKU']
            supplier_id = request.session.get("supplier_id")
            price = form.cleaned_data['price']
            delv = form.cleaned_data['deliverable_days']
            data = Products.objects.filter(SKU=SKU).first()
            productid = data.id
            data.is_active = False
            data.save()
            x = form.save(commit=False)
            x.product_id = productid
            x.save()
            Product_exist = BestProductsSupplier.objects.filter(
                product_id=productid).first()

            if not Product_exist:
                best_prod = BestProductsSupplier(
                    product_id=productid, supplier_id=supplier_id, lowest_price=price, lowest_delivery_time=delv)
                best_prod.save()
                return redirect('wayrem_supplier:supplier_product_list')
            price = float(price)
            old_price = float(Product_exist.lowest_price)
            if old_price > price:
                Product_exist.lowest_price = price
                Product_exist.supplier_id = supplier_id
                Product_exist.lowest_delivery_time = delv
                Product_exist.save()
                return redirect('wayrem_supplier:supplier_product_list')
            if old_price == price:
                best_prod = BestProductsSupplier(
                    product_id=productid, supplier_id=supplier_id, lowest_price=price, lowest_delivery_time=delv)
                best_prod.save()
                return redirect('wayrem_supplier:supplier_product_list')
            if old_price < price:
                pass
            return redirect('wayrem_supplier:supplier_product_list')
        else:
            print("Invalid")
            return redirect('wayrem_supplier:supplier_product_list')


class DeleteProduct(View):
    def post(self, request):
        productid = request.POST.get('product_id')
        products = SupplierProducts.objects.get(id=productid)
        products.delete()
        return redirect('wayrem_supplier:supplier_product_list')


def supplier_product_update(request, id=None, *args, **kwargs):
    print(id)
    if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
    if request.method == "POST":
        sup_prod = SupplierProducts.objects.get(id=id)
        form = SupplierProductForm(
            request.POST or None, instance=sup_prod)
        if form.is_valid():
            print("FORM")
            SKU = form.cleaned_data['SKU']
            product_name = form.cleaned_data['product_name']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            available = form.cleaned_data['available']
            deliverable_days = form.cleaned_data['deliverable_days']
            sup_prod.SKU = SKU
            sup_prod.product_name = product_name
            sup_prod.quantity = quantity
            sup_prod.price = price
            sup_prod.available = available
            sup_prod.deliverable_days = deliverable_days
            sup_prod.save()
            print("Here")
            return redirect('wayrem_supplier:supplier_product_list')
    sup_prod = SupplierProducts.objects.get(id=id)
    form = SupplierProductForm(instance=sup_prod)
    return render(request, 'supplier_product_update.html', {'form': form, 'id': sup_prod.id})


def supplier_product_excel(request):
    return generate_excel("product_suppliers", "supplier_products")
