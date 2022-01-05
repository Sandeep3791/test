#!/usr/bin/env python
# coding: utf-8
from django import template
from django.template import Context
from datetime import date, datetime
from wayrem_admin.models_orders import OrderDetails,OrderTransactions,OrderDetails
from django.db.models import Sum
register = template.Library()


@register.filter(name='total_items')
def total_items(order_id):
    total_items_count=OrderDetails.objects.filter(order=order_id).aggregate(Sum('quantity'))
    if total_items_count:
        total_items=total_items_count['quantity__sum']
    else:
        total_items=0
    if total_items is None:
        total_items=0

    return total_items

@register.filter(name='add_product_items')
def add_product_items(var1,var2):
    price=var1+var2
    return price 

@register.filter(name='payment_status')
def payment_status(order_id):
    order_transaction=OrderTransactions.objects.filter(order=order_id).first()
    return order_transaction.payment_status

@register.filter(name='transaction_invoice')
def transaction_invoice(order_id):
    order_transaction=OrderTransactions.objects.filter(order=order_id).first()
    return order_transaction.invoices_id

@register.filter(name='unit_product_total')
def unit_product_total(ord_detail_id):
    ord_det_id=OrderDetails.objects.get(id=ord_detail_id)
    total_amount=((float(ord_det_id.price) + float(ord_det_id.item_margin))*float(ord_det_id.quantity))-float(ord_det_id.discount)
    return total_amount


