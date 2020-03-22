from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from .serializers import ProductSerializer, CategorySerializer
from rest_framework import generics

# Create your views here.
def product_list(request, category_slug=None):
    category=None
    categories=Category.objects.all()
    products=Product.objects.filter(available=True)
    if category_slug:
        category=get_object_or_404(Category, slug=category_slug)
        products=products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category': category, 'categories':categories, 'products':products})

def product_detail(request, id, slug):
    product=get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form=CartAddProductForm()
    return render(request, 'shop/product/detail.html', {'product':product, 'cart_product_form':cart_product_form})

#API Views
class ProductList(generics.ListAPIView):
    #queryset=Product.objects.all()
    serializer_class=ProductSerializer

    def get_queryset(self):
        category=None
        categories=Category.objects.all()
        products=Product.objects.filter(available=True)
        category_slug = self.request.query_params.get('category_slug', None)
        if category_slug is not None:
            category=get_object_or_404(Category, slug=category_slug)
            products=products.filter(category=category)
        queryset=products
        return queryset

class ProductDetail(generics.RetrieveAPIView):
    queryset=Product.objects.filter(available=True)
    serializer_class=ProductSerializer

class CategoryList(generics.ListAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
