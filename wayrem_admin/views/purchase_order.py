from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import PurchaseOrder, Products, Supplier
from wayrem_admin.forms import POForm, POEditForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.services import inst_Product, inst_Supplier, delSession
from wayrem_admin.export import generate_excel
from wayrem_admin.decorators import role_required
import datetime
import uuid
from django.db import connection


def po_excel(request):
    return generate_excel("po_master", "purchase_order")


@role_required('Purchase Order Add')
def create_purchase_order(request):
    if request.method == "POST":
        form = POForm(request.POST or None, request.FILES or None)
        if 'addMore' in request.POST:
            if request.POST['product_name'] == "":
                messages.error(request, "Please select a Product!")
                return redirect("wayrem_admin:create_po")
            product_id = request.POST['product_name']
            product_qty = request.POST['product_qty']
            name = inst_Product(product_id)
            if any(e[0] == product_id for e in request.session.get('products')):
                messages.error(request, "Product already added!")
                return redirect("wayrem_admin:create_po")
            x = (product_id, name.name, product_qty)
            request.session['products'].append(x)
            po = request.session['products']
            request.session['supplier_company'] = request.POST['supplier_name']
            request.session.modified = True
            print('add more')
            return render(request, "po_step1.html", {'form': form, 'po': po})
        elif 'send' in request.POST:
            if request.POST['supplier_name'] == '':
                messages.error(request, "Please Select Supplier!")
                return render(request, "po_step1.html", {'form': form, 'po': request.session['products']})
            if request.session['products'] == []:
                messages.error(request, "Please select some Products!")
                return redirect("wayrem_admin:create_po")
            else:
                print("supplier")
                supplier_name = inst_Supplier(request.POST['supplier_name'])
                x = request.POST['supplier_name']
                # random_no = random.randint(1000, 99999)
                po_id = uuid.uuid4()
                # po_name = "PO"+str(random_no)
                today = str(datetime.date.today())
                curr_year = int(today[:4])
                curr_month = int(today[5:7])
                curr_date = int(today[8:10])
                po = PurchaseOrder.objects.all()
                aa = po.count()+1
                q = ["{0:04}".format(aa)]
                p = q[0]
                po_name = "PO/"+str(curr_date) + \
                    str(curr_month)+str(curr_year)+'/'+p

                for data in request.session['products']:
                    supp_po_id = uuid.uuid4()
                    print(data)
                    product_instance = inst_Product(data[0])
                    product_qty = data[2]
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"INSERT INTO {supplier_name.username}_purchase_order(`id`,`po_id`,`po_name`,`product_qty`,`product_name_id`,`supplier_name_id`) VALUES('{supp_po_id}','{po_id}','{po_name}','{data[2]}','{product_instance.id.hex}','{x.replace('-','')}');")
                        product_order = PurchaseOrder(
                            po_id=po_id, po_name=po_name, product_name=product_instance, product_qty=product_qty, supplier_name=supplier_name)
                    product_order.save()
                messages.success(
                    request, f"Purchase Order Created Successfully!")
                request.session['products'] = []
                return redirect('wayrem_admin:polist')
        else:
            print("Invalid")
    else:
        if request.GET.get('supplier'):
            form = POForm(
                initial={"supplier_name": request.GET.get('supplier')})
        elif request.GET.get('product'):
            form = POForm(
                initial={"product_name": request.GET.get('product')})
        elif request.GET.get('suprod'):
            x = request.GET.get('suprod').split('?')
            product = Products.objects.get(SKU=x[1])
            form = POForm(
                initial={"product_name": product, "supplier_name": x[0]})
        else:
            form = POForm(
                initial={'supplier_name': request.session.get('supplier_company', None)})
    po = request.session.get('products', None)
    return render(request, "po_step1.html", {'form': form, "po": po})


def delete_inserted_item(request, id=None):
    product = request.session.get("products")
    for index, num_list in enumerate(product):
        if num_list[0] == id:
            del product[index]
            break
    print(product)
    request.session["products"] = product
    return redirect('wayrem_admin:create_po')


class POList(View):
    template_name = "po_list.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Purchase Order View'))
    def get(self, request, format=None):
        delSession(request)
        polist = PurchaseOrder.objects.values(
            'po_id', 'po_name', 'supplier_name', 'status').distinct()
        pol = []
        for i in polist:
            obj = Supplier.objects.filter(
                id=i['supplier_name']).first()
            pol.append(obj.username)
        mylist = zip(polist, pol)
        # polist = PurchaseOrder.objects.values_list('po_id').distinct()
        # polist = PurchaseOrder.objects.distinct('po_id')
        request.session['products'] = []
        return render(request, self.template_name, {"userlist": mylist})


class DeletePO(View):

    @method_decorator(role_required('Purchase Order Delete'))
    def post(self, request):
        po_id = request.POST.get('po_id')
        po_obj = PurchaseOrder.objects.filter(po_id=po_id).all()
        po_obj.delete()
        return redirect('wayrem_admin:polist')


@role_required('Purchase Order View')
def viewpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    return render(request, 'view_po.html', {"po": po})


@role_required('Purchase Order Edit')
def editpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        if 'addMore' in request.POST:
            form = POEditForm()
            if request.POST['product_name'] == "":
                messages.error(request, "Please select a Product!")
                return render(request, 'edit_po.html', {"po": po, "form": form})
            product = request.POST.get('product_name')
            name = inst_Product(product)
            quantity = request.POST.get('product_qty')
            supplier = po[0].supplier_name
            po_id = po[0].po_id
            poname = request.POST.get('poname')
            new = PurchaseOrder(
                po_name=poname, product_name=name, product_qty=quantity, supplier_name=supplier, po_id=po_id)
            new.save()
            return render(request, 'edit_po.html', {"po": po, "form": form})

        count = 1
        for item in po:
            item.po_name = request.POST.get('poname')
            item.product_qty = request.POST.get(f'prodqty{count}')
            item.save()
            count += 1
        return redirect('wayrem_admin:polist')
    else:
        form = POEditForm()
    return render(request, 'edit_po.html', {"po": po, "form": form})


@role_required('Purchase Order Edit')
def statuspo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        status = request.POST.get('status')
        po.update(status=status)
        return redirect('wayrem_admin:polist')
    return redirect('wayrem_admin:polist')
