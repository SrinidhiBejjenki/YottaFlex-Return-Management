
from django.test import TestCase
from returns.models import (
    Customer,
    Order,
    OrderLine,
    ReturnRequest,
    ReturnLine,
    ReturnAuthorization,
)


class ReturnFlowModelTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id="TEST-CUST-001",
            name="Test Customer",
            email="test@example.com",
            phone="9876543210"
        )

        self.order = Order.objects.create(
            order_id="TEST-ORD-001",
            customer=self.customer,
            order_date="2026-10-20T10:00:00Z",
            total_amount=1000,
            status="PLACED"
        )

        self.order_line = OrderLine.objects.create(
            order=self.order,
            product_name="Test Product",
            quantity=2,
            unit_price=500
        )

    def test_customer_creation(self):
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(self.customer.name, "Test Customer")

    def test_order_customer_relationship(self):
        self.assertEqual(self.order.customer, self.customer)

    def test_order_line_creation(self):
        self.assertEqual(self.order_line.quantity, 2)
        self.assertEqual(self.order_line.unit_price, 500)

    def test_return_request_creation(self):
        return_request = ReturnRequest.objects.create(
            return_id="TEST-RET-001",
            order=self.order,
            reason="Damaged product",
            status="REQUESTED"
        )

        self.assertEqual(return_request.order, self.order)

    def test_authorization_creation(self):
        return_request = ReturnRequest.objects.create(
            return_id="TEST-RET-002",
            order=self.order,
            reason="Wrong product",
            status="REQUESTED"
        )

        authorization = ReturnAuthorization.objects.create(
            authorization_id="TEST-AUTH-001",
            return_request=return_request,
            approved=True,
            status="APPROVED"
        )

        self.assertTrue(authorization.approved)
