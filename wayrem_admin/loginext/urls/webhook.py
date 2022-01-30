from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from wayrem_admin.loginext.views import webhook_order_views

urlpatterns = [
    path('order/createrequest',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'createorderrequest'}),name='createrequest'),
    path('order/create',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'createorder'}),name='createorder'),
    path('order/updateorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'updateorder'}),name='updateorder'),
    path('order/orderstatusupdate',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'orderstatusupdate'}),name='orderstatusupdate'),
    path('order/acceptedorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'acceptedorder'}),name='acceptedorder'),
    path('order/rejectedorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'rejectedorder'}),name='rejectedorder'),
    path('order/cancelorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'cancelorder'}),name='cancelorder'),
    path('order/checkinorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'checkinorder'}),name='checkinorder'),
    
    #path('order/loaditemsorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'get': 'loaditemsorder'}),name='loaditemsorder'),
    #path('order/loadcompleteorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'get': 'loadcompleteorder'}),name='loadcompleteorder'),
    
    path('order/deliveredorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'deliveredorder'}),name='deliveredorder'),
    path('order/attempteddeliveryorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'attempteddeliveryorder'}),name='attempteddeliveryorder'),
    
    path('order/partiallydeliveredorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'partiallydeliveredorder'}),name='partiallydeliveredorder'),
    path('order/pickeduporder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'pickeduporder'}),name='pickeduporder'),
    path('order/orderattemptedpickuporder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'orderattemptedpickuporder'}),name='orderattemptedpickuporder'),
    #path('order/orderallocationstoppedorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'get': 'orderallocationstoppedorder'}),name='orderallocationstoppedorder'),
]
