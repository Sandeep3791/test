import imp
from django.urls import path
from wayrem_admin import views


urlpatterns = [
    path('credits-create/', views.CreditCreate.as_view(), name='create_credit'),
    path('credits-list/', views.CreditsList.as_view(), name='credits_list'),
    path('credit/<int:credit_pk>', views.CreditUpdate.as_view(),
         name='update_credit'),
    path('credit/view/<int:credit_pk>',
         views.CreditView.as_view(), name='view_credit'),
    path('credit/assign/<int:id>',
         views.creditAssign, name='assign_credit')

]
