from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('returns/', views.return_list, name='return_list'),
    path('refunds/', views.refund_list, name='refund_list'),
]