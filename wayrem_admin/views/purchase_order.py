from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import PurchaseOrder, Products, Supplier
from wayrem_admin.forms import POForm, POEditForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.services import inst_Product, inst_Supplier
from wayrem_admin.export import generate_excel
import random
import uuid


def po_excel(request):
    return generate_excel("po_master", "purchase_order")


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
            x = (product_id, name.product_name, product_qty)
            request.session['products'].append(x)
            po = request.session['products']
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
                random_no = random.randint(1000, 99999)
                po_id = uuid.uuid4()
                po_name = "PO"+str(random_no)
                for data in request.session['products']:
                    print(data)
                    product_instance = inst_Product(data[0])
                    product_qty = data[2]
                    product_order = PurchaseOrder(
                        po_id=po_id, po_name=po_name, product_name=product_instance, product_qty=product_qty, supplier_name=supplier_name)
                    product_order.save()
                messages.success(
                    request, f"Purchase Order Created Successfully!")
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
            form = POForm()
    request.session['products'] = []
    return render(request, "po_step1.html", {'form': form})


class POList(View):
    template_name = "po_list.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
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
        return render(request, self.template_name, {"userlist": mylist})


class DeletePO(View):
    def post(self, request):
        po_id = request.POST.get('po_id')
        po_obj = PurchaseOrder.objects.filter(po_id=po_id).all()
        po_obj.delete()
        return redirect('wayrem_admin:polist')


class POStatus(View):
    def post(self, request):
        po_id = request.POST.get('po_id')
        po_obj = PurchaseOrder.objects.filter(po_id=po_id).all()
        if po_obj[0].is_active:
            po_obj.update(is_active=False)
        else:
            po_obj.update(is_active=True)
        return redirect('wayrem_admin:polist')


def viewpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    return render(request, 'view_po.html', {"po": po})


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


def statuspo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        status = request.POST.get('status')
        po.update(status=status)
        return redirect('wayrem_admin:polist')
    return redirect('wayrem_admin:polist')
