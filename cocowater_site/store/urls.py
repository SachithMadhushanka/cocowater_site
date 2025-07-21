from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('cart/', views.cart, name="cart"),
    path('add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('update/<int:product_id>/', views.update_cart, name="update_cart"),
    path('remove/<int:product_id>/', views.remove_from_cart, name="remove_from_cart"),
   # path('checkout/', views.checkout, name="checkout"),
   path('success/<int:order_id>/', views.payment_success, name='payment_success'),
]
