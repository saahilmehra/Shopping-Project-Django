from django.urls import path
from . import views

app_name='payment'

urlpatterns=[
    path('process/', views.payment_process, name='process'),
    path('done/', views.payment_done, name='done'),
    path('canceled/', views.payment_canceled, name='canceled'),

    #API
    path('api/client_token/', views.ClientToken.as_view()),
    path('api/process/<int:pk>/', views.PaymentProcess.as_view()),
]
