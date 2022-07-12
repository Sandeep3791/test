import django_filters
from wayrem_admin.models import Wallet
from wayrem_admin.utils.constants import *



class WalletFilter(django_filters.FilterSet):
    class Meta:
        model=Wallet
        fields = ['amount','payment_type_id','transaction_type_id','order_id','customer_id','created']