from rest_framework import serializers
from orders.models import Order

class PaymentProcessSerializer(serializers.ModelSerializer):
    nonce=serializers.CharField(max_length=500)
    class Meta:
        model=Order
        fields=['nonce']
