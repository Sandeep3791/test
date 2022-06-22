from wayrem_admin.models import ShippingLoginextNotification
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer


class LogiNextWeebHookOrderSerializer(ModelSerializer):
    class Meta:
        model = ShippingLoginextNotification
        fields = ('notification_type', 'reference_id')
