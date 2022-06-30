from django.urls import path
from wayrem_admin.views.credits import *


urlpatterns = [
    path('credits-create/', CreditCreate.as_view(), name='create_credit'),
    path('credits-list/', CreditsList.as_view(), name='credits_list'),
    path('credit/<int:credit_pk>', CreditUpdate.as_view(),
         name='update_credit'),
    path('credit/view/<int:credit_pk>',
         CreditView.as_view(), name='view_credit'),
    path('credit/assign/<int:id>',
         creditAssign, name='assign_credit')

]
