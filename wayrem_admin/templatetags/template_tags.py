from typing import Set
from django import template
from wayrem_admin.models import Settings
register = template.Library()


@register.simple_tag()
def net_value(unit_price, qty, *args, **kwargs):
    # you would need to do any localization of the result here
    net_amt = float(qty) * float(unit_price)
    return "{:.2f}".format(net_amt)


@register.simple_tag()
def vat_amt(unit_price, qty, *args, **kwargs):
    obj = Settings.objects.filter(key="setting_vat").first()
    vat = float(obj.value)
    # vat = float(vat[:-1])
    # you would need to do any localization of the result here
    total_amt = float(qty) * float(unit_price)
    vat_float = (total_amt/100)*vat
    return "{:.2f}".format(vat_float)


@register.simple_tag()
def net_vat_amt(unit_price, qty, *args, **kwargs):
    obj = Settings.objects.filter(key="setting_vat").first()
    vat = float(obj.value)
    # vat = float(vat[:-1])
    # you would need to do any localization of the result here
    total_amt = float(qty) * float(unit_price)
    vat_amt = (total_amt/100)*vat
    net = total_amt+vat_amt
    return "{:.2f}".format(net)


@register.simple_tag()
def image_tag(value, *args, **kwargs):
    if value:
        return value.split("/")[-1]
    else:
        x = False
        return x
