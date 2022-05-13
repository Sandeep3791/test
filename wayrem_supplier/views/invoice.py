from django.shortcuts import render, redirect
from django.views import View
from wayrem_supplier.models import PurchaseOrder, Invoice
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
import base64
from django.contrib import messages
import uuid
from wayrem_supplier.export import generate_excel
import constant
from django.http import HttpResponse
import os
from django.apps import apps





class PoInvoiceList(View):
    template_name = "polistforinvoice.html"    
    def get(self, request, format=None):
        if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
        supplier_name = request.session.get('supplier')
        supplier_id = request.session.get("supplier_id")
        # supplierid = request.session['supplier_id']
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT po_name FROM {constant.database}.{supplier_name}_Invoice where supplier_name="{supplier_name}";')
            a=cursor.fetchall()
            v = list(a)
            ab = [i[0] for i in v]
            y = tuple(ab)
            print(ab)
        with connection.cursor() as cursor:
            if len(ab)==0:
                prodlist = tuple()
                cursor.execute(f'SELECT * FROM {constant.database}.po_master where supplier_name_id = "{supplier_id}" group by po_name')
                prodlist= cursor.fetchall()
            elif len(ab)==1:
                cursor.execute(f'SELECT * FROM {constant.database}.po_master where po_name != "{ab[0]}" AND supplier_name_id = "{supplier_id}" group by po_name')
                prodlist= cursor.fetchall()
            else:
                cursor.execute(f'SELECT * FROM {constant.database}.po_master where po_name NOT IN {y} AND supplier_name_id = "{supplier_id}" group by po_name')
                prodlist= cursor.fetchall()                
        paginator = Paginator(prodlist, 25)
        page = request.GET.get('page')
        try:
            poinvoicelist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            poinvoicelist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            poinvoicelist = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {"poinvoicelist":poinvoicelist}) 


class InvoiceList(View):
    template_name = "invoicelist.html"
    
    def get(self, request, format=None):
        if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
        supplier_name = request.session.get('supplier')
        supplier_id = request.session.get('supplier_id')
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT invoice_no, po_name, status, created_at FROM {supplier_name}_Invoice') 
            rec = cursor.fetchall()     
        data = PurchaseOrder.objects.filter(supplier_name = supplier_id).all()  
        poinvlist = list(data.values('po_id','po_name').distinct())
        paginator = Paginator(rec, 25)
        page = request.GET.get('page')
        try:
            recd = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            recd = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            recd = paginator.page(paginator.num_pages)   
        # mydata = zip(poinvlist, recd)         
        return render(request, self.template_name, {'recd':recd})

def upload_invoice(request):
    if request.method == 'POST':
        po_name = request.POST.get('po_name')
        fileone = request.FILES["myFileInput"]  
        # read textfile into string 
        mytextstring = fileone.read()
        # change text into a binary array
        binarray = base64.b64encode(mytextstring)
        # filetwo=convertToBinaryData(fileone)         
        supplier_id = request.session.get("supplier_id")
        supplier_name = request.session.get('supplier')
        
        import datetime
        today = str(datetime.date.today())
        curr_year = int(today[:4])
        curr_month = int(today[5:7])
        curr_date = int(today[8:10])
        po = Invoice.objects.all()
        aa = po.count()+1
        q = ["{0:04}".format(aa)]
        p = q[0]
        invoice_name = "INV/"+str(curr_date) +\
            str(curr_month)+str(curr_year)+'/'+p
        v = Invoice.objects.filter(po_name=po_name).first()
        if v:
            messages.error(request, "This invoice already created!")
            print('This Data is already in your data base.')
            return redirect('wayrem_supplier:invoicelist')  
        binarray = str(binarray,'utf-8')
         

        invo = Invoice(po_name=po_name, invoice_no=invoice_name, supplier_name=supplier_name, file = fileone, status='released' )
        invo.save()
        invoice_id = invo.invoice_id
        supplier_invoice_model =  'Invoice_' + str(supplier_name)  
        supplier_invoice = apps.get_model(app_label='wayrem_supplier', model_name=supplier_invoice_model)
        invoice_upload = supplier_invoice(po_name=po_name, invoice_no=invoice_name, supplier_name=supplier_name, file = fileone, status='released' )
        invoice_upload.save()
        # with connection.cursor() as cursor:
        #     cursor.execute(f"INSERT INTO {supplier_name}_Invoice(`invoice_id`,`invoice_no`,`po_name`,`file`,`supplier_name`,`status`) VALUES('{invoice_id}','{invoice_name}','{po_name}','{binarray}','{supplier_name}','{'released'}');")   
        return redirect('wayrem_supplier:invoicelist')    


def status_invoice(request):
    # po = PurchaseOrder.objects.filter(po_id=id).all()
    id=request.GET.get('id')
    supplier_name = request.session.get('supplier')
    if request.method == "POST":
        status = request.POST.get('status') 
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE `{supplier_name}_Invoice` SET `status` = '{status}' WHERE `invoice_no` = '{id}';") 
            records = cursor.fetchall()           
        # records.update(status=status)
        return redirect('wayrem_supplier:invoicelist')
    return redirect('wayrem_supplier:invoicelist') 


class DeleteInvoice(View):
    def post(self, request):
        productid = request.POST.get('invo_id')
        supplier_name = request.session.get('supplier')
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM `{supplier_name}_Invoice` WHERE `invoice_no` = '{productid}';")         
        return redirect('wayrem_supplier:invoicelist')

def invoice_excel(request):
    supplier_name = request.session.get('supplier')
    return generate_excel(f"{supplier_name}_Invoice", "supplier_products")


class DownloadInvoice(View):
    def get(self, request):
        try:
            number = request.GET.get('invoice_no')
            invoice = number
            # invoice="INV/26112021/0001"
            contents = Invoice.objects.get(po_name=invoice)
            filename = contents.file.url.split('/')[-1]
            response = HttpResponse(contents.file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
        except:
            messages.error(request, "Something went wrong!")
            return redirect('wayrem_supplier:purchase_order_list')