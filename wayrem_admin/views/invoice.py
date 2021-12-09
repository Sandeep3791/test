import codecs
from django.views import View
from wayrem_admin.models import Invoice
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class InvoiceList(View):
    template_name = "invoicelist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        userlist = Invoice.objects.all()
        return render(request, self.template_name, {"userlist": userlist})

import base64
from io import BytesIO
from django.http import HttpResponse
from wsgiref.util import FileWrapper

# class DownloadInvoice(View):
#     def get(self,request):
#         number = request.GET.get('invoice_no')
#         invoice=number
#         # invoice="INV/26112021/0001"
#         contents = Invoice.objects.get(invoice_no=invoice).file
#         buffer = BytesIO()
#         content=base64.b64decode(contents)
#         buffer.write(content)
#         filename = invoice.replace('/','-')+ '.pdf'
#         response = HttpResponse(
#             buffer.getvalue(),
#             content_type="application/pdf",
#         )
#         response['Content-Disposition'] = f'inline;filename={filename}.pdf'
#         return response
        # with open(filename, "wb") as f:
        #     f.write(codecs.decode(contents, "base64"))
        # response = HttpResponse(filename)
        # return response


        #     response = HttpResponse(
        #     f.getvalue(),
        #     content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        # )
        # response['Content-Disposition'] = 'attachment; filename=%s' % filename
        # return response

class DownloadInvoice(View):
    def get(self,request):
        number = request.GET.get('invoice_no')
        invoice=number
        # invoice="INV/26112021/0001"
        contents = Invoice.objects.get(invoice_no=invoice)
        filename = contents.file.name.split('/')[-1]
        response = HttpResponse(contents.file.url)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response