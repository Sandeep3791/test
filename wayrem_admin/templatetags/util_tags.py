#!/usr/bin/env python
# coding: utf-8
from django.shortcuts import get_object_or_404
from wayrem_admin.models import Products
from wayrem_admin.models.orders import Orders
from wayrem_admin.services import inst_SupplierProduct
from django import template
from datetime import date, datetime
from wayrem_admin.models import OrderDetails, OrderTransactions, OrderDetails
from wayrem_admin.models import ForecastProduct
from django.db.models import Sum
register = template.Library()


@register.filter(name='display_discount_price')
def display_discount_price(order_detail_id):
    order_details = OrderDetails.objects.filter(id=order_detail_id).first()
    total_amount = float(order_details.price) + \
        float(order_details.item_margin) - float(order_details.discount)
    return round(total_amount, 2)


@register.filter(name='display_discount_price_qty')
def display_discount_price_qty(order_detail_id):
    order_details = OrderDetails.objects.filter(id=order_detail_id).first()
    total_amount = (float(order_details.price) + float(order_details.item_margin) -
                    float(order_details.discount)) * float(order_details.quantity)
    return round(total_amount, 2)


@register.filter(name='total_items')
def total_items(order_id):
    total_items_count = OrderDetails.objects.filter(
        order=order_id).aggregate(Sum('quantity'))
    if total_items_count:
        total_items = total_items_count['quantity__sum']
    else:
        total_items = 0
    if total_items is None:
        total_items = 0

    return total_items


@register.filter(name='add_product_items')
def add_product_items(var1, var2):
    price = var1+var2
    return price


@register.filter(name='payment_status')
def payment_status(order_id):
    # return order_id
    order_transaction = OrderTransactions.objects.filter(
        order=order_id).first()
    if order_transaction:
        return order_transaction.payment_status
    else:
        return ""


@register.filter(name='payment_type')
def payment_type(order_id):
    # return order_id
    order_transaction = OrderTransactions.objects.filter(
        order=order_id).first()
    if order_transaction:
        return order_transaction.payment_mode
    else:
        return ""


@register.filter(name='transaction_invoice')
def transaction_invoice(order_id):
    if order_id is None:
        return ""
    order_transaction = OrderTransactions.objects.filter(
        order=order_id).first()
    if order_transaction:
        return order_transaction.invoices_id
    else:
        return ""


@register.filter(name='unit_product_total')
def unit_product_total(ord_detail_id):
    ord_det_id = OrderDetails.objects.get(id=ord_detail_id)
    total_amount = ((float(ord_det_id.price) + float(ord_det_id.item_margin))
                    * float(ord_det_id.quantity))-float(ord_det_id.discount)
    return total_amount


@register.filter(name='forecast_quantity')
def forecast_quantity(no_of_day, product_id):
    # print(no_of_day)
    # print(product_id)
    x = inst_SupplierProduct(product_id)
    print(x.SKU)
    product_SKU = x.SKU
    product_id = Products.objects.get(SKU=product_SKU)
    get_forecast_quantity = ForecastProduct.objects.values("forecast_quantity").filter(
        forecast_jobtype_id=no_of_day, product_id=product_id.id, created_at__gte=date.today()).order_by("-id").first()
    print(product_id.id)
    print(ForecastProduct.objects.values("forecast_quantity").filter(
        forecast_jobtype_id=no_of_day, product_id=product_id.id, created_at__gte=date.today()).order_by("-id").query)
    if get_forecast_quantity is None:
        return 0
    else:
        return get_forecast_quantity['forecast_quantity']
    return product_id


@register.filter(name='inventory_customer')
def inventory_customer(order_id):
    # return order_id
    order = get_object_or_404(Orders, pk=order_id)
    if order:
        return (f"{order.customer.first_name} {order.customer.last_name}")
    else:
        return "-"


@register.filter(name="transaction_type")
def transaction_type(transaction_type_id):
    if transaction_type_id == 1:
        return "Dr"
    else:
        return "Cr"

@register.filter(name="get_order_reference")
def get_order_reference(order_id):
    order_details=Orders.objects.filter(id=order_id).first()
    if order_details is not None:
        return order_details.ref_number 
    else:
        return ""

@register.filter(name="unittype")
def unittype(unit_id):
    return 1