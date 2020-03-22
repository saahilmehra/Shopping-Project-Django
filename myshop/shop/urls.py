from django.urls import path
from . import views

app_name='shop'

urlpatterns=[
    #API urlpatterns
    path('api/', views.ProductList.as_view()),
    path('categories/', views.CategoryList.as_view()),
    path('api/<int:pk>/', views.ProductDetail.as_view()),
    #Website urlpatterns
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]
