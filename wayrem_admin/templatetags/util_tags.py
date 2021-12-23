#!/usr/bin/env python
# coding: utf-8
from django import template
from django.template import Context
from datetime import date, datetime
from wayrem_admin.models_orders import OrderDetails
register = template.Library()


@register.filter(name='total_items')
def total_items(order_id):
    total_items = OrderDetails.objects.filter(order=order_id).count()
    return total_items