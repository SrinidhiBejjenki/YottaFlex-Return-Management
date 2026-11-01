
from django.shortcuts import render, get_object_or_404

from .models import (
    Customer,
    Order,
    ReturnRequest,
    Refund,
)


# Home page
def home(request):
    return render(request, 'home.html')


# Customer list
def customer_list(request):
    customers = Customer.objects.all()

    return render(request, 'customers.html', {
        'customers': customers
    })


# Order list
def order_list(request):
    orders = Order.objects.select_related('customer').all()

    return render(request, 'orders.html', {
        'orders': orders
    })


# Order details
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    return render(request, 'order_detail.html', {
        'order': order
    })


# Return request list
def return_list(request):
    returns = ReturnRequest.objects.select_related('order').all()

    return render(request, 'returns.html', {
        'returns': returns
    })


# Refund list
def refund_list(request):
    refunds = Refund.objects.select_related('return_request').all()

    return render(request, 'refunds.html', {
        'refunds': refunds
    })


# Dashboard
def dashboard(request):
    context = {
        'total_customers': Customer.objects.count(),
        'total_orders': Order.objects.count(),
        'total_returns': ReturnRequest.objects.count(),
        'total_refunds': Refund.objects.count(),
    }

    return render(request, 'dashboard.html', context)
