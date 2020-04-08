from rest_framework import serializers
from .models import Order, OrderItem
from shop.models import Product

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

class ItemsSerializer(serializers.ModelSerializer):
    model=OrderItem
    items = serializers.CharField(read_only=True)
    class Meta:
        model=OrderItem
        fields='__all__'

class ItemsSaveSerializer(serializers.ModelSerializer):
    model=Order
    items=ItemsSerializer(many=True, read_only=True)

    class Meta:
        model=Order
        fields=('id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'items',)

    def create(self, validated_data):
        request=self.context.get('request')
        first_name=request.data.get('first_name', None)
        last_name=request.data.get('last_name', None)
        email=request.data.get('email', None)
        address=request.data.get('address', None)
        postal_code=request.data.get('postal_code', None)
        city=request.data.get('city', None)
        order=Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city
        )

        #obj1=Order.objects.get(id=order)
        items_data=request.data.get('items', [])

        for item in items_data:
            p=item['product']
            p2=Product.objects.get(id=p)
            obj_temp=OrderItem.objects.create(
                #order=obj1,
                order=order,
                product=p2,
                price=item['price'],
                quantity=item['quantity']
            )

        return Order.objects.all().get(id=order.id)
