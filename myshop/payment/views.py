import braintree
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import weasyprint
from io import BytesIO

from .serializers import PaymentProcessSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.http import Http404

# Create your views here.
def payment_process(request):
    order_id=request.session.get('order_id')
    order=get_object_or_404(Order, id=order_id)

    if request.method=='POST':
        #retrieve nounce
        nonce=request.POST.get('payment_method_nonce', None)
        #create and submit transaction
        result=braintree.Transaction.sale({
            'amount':'{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce':nonce,
            'options':{
                'submit_for_settlement':True
            }
        })
        if result.is_success:
            #mark the order as paid
            order.paid=True
            #store the unique  transaction id
            order.braintree_id=result.transaction.id
            order.save()
            #create invoice e-mail
            subject="Smehra's Shop - Invoice no. {}".format(order.id)
            message='Please, find the attached invoice for your recent purchase.'
            email=EmailMessage(subject, message, 'testemailsmsm@gmail.com', [order.email])
            #generate PDF
            html=render_to_string('orders/order/pdf.html', {'order':order})
            out=BytesIO()
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

            #attach PDF files
            email.attach('order_{}.pdf'.format(order.id), out.getvalue(), 'application/pdf')
            #send e-mail
            email.send()

            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        #generate token
        client_token=braintree.ClientToken.generate()
        return render(request, 'payment/process.html', {'order':order, 'client_token':client_token})

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')

#API
class ClientToken(APIView):
    def get(self, request):
        client_token=braintree.ClientToken.generate()
        return Response({'client_token': client_token})

class PaymentProcess(APIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        order=self.get_object(pk)
        serializer = PaymentProcessSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            nonce=serializer.data['nonce']

            result=braintree.Transaction.sale({
                'amount':'{:.2f}'.format(order.get_total_cost()),
                'payment_method_nonce':nonce,
                'options':{
                    'submit_for_settlement':True
                }
            })
            if result.is_success:
                #mark the order as paid
                order.paid=True
                #store the unique  transaction id
                order.braintree_id=result.transaction.id
                order.save()

                #create invoice e-mail
                subject="Smehra's Shop - Invoice no. {}".format(order.id)
                message='Please, find the attached invoice for your recent purchase.'
                email=EmailMessage(subject, message, 'testemailsmsm@gmail.com', [order.email])
                #generate PDF
                html=render_to_string('orders/order/pdf.html', {'order':order})
                out=BytesIO()
                stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
                weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

                #attach PDF files
                email.attach('order_{}.pdf'.format(order.id), out.getvalue(), 'application/pdf')
                #send e-mail
                email.send()

                return Response({'payment_status': "success"})
            else:
                return Response({'payment_status': "failed"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
