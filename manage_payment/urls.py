
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/new/', new_subscription, name='new_subscription'),
    path('check/transaction/', check_transaction, name='check_transaction'),
    path('get/transaction/state/', get_subscription_state, name='get_transaction_state'),
    path('sim800l/get/first/validated/transaction/', get_first_validated_transaction, name='get_first_validated_transaction'),
    path('sim800l/<int:pk>/change/validated/transaction/', change_state_of_transaction, name='change_state_transaction'),
    path('sim800l/get/messages/', sim800l_get_messages, name='get_all_messages'),
    path('sim800l/update/message/<int:pk>/', sim800l_update_message, name='get_update_messages'),
    path('update/transaction/state/', update_subscription_state, name='update_transaction_state'),
    path('sim800l/add/transaction/<str:date>/<str:id_trans>/<str:op>/<str:amount>/', add_transaction, name='add_transaction'),
    path('sim800l/get/transactions/<str:prefix>/', sim800l_get_transactions, name='sim800l_get_transactions'),
    path('sim800l/update/transaction/<int:pk>/', sim800l_update_transactions, name='sim800l_update_transaction'),
    path('portal/captive/login/', auth_views.LoginView.as_view(), name='login')
]