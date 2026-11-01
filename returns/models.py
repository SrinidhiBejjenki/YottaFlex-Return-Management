from django.db import models
class Customer(models.Model):
    customer_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    order_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, default="PLACED")

    def __str__(self):
        return self.order_id

class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_lines"
    )
    product_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order.order_id} - {self.product_name}"

class ReturnRequest(models.Model):
    return_id = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="return_requests"
    )
    request_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default="REQUESTED")

    def __str__(self):
        return self.return_id

class ReturnLine(models.Model):
    return_request = models.ForeignKey(
        ReturnRequest, on_delete=models.CASCADE, related_name="return_lines"
    )
    order_line = models.ForeignKey(
        OrderLine, on_delete=models.CASCADE, related_name="return_lines"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.return_request.return_id} - {self.order_line.product_name}"


class ReturnAuthorization(models.Model):
    authorization_id = models.CharField(max_length=30, unique=True)
    return_request = models.OneToOneField(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name="authorization"
    )
    approved = models.BooleanField(default=False)
    authorized_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="PENDING")


class ReturnShipment(models.Model):
    shipment_id = models.CharField(max_length=30, unique=True)
    authorization = models.ForeignKey(
        ReturnAuthorization,
        on_delete=models.CASCADE,
        related_name="shipments"
    )
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    received_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="CREATED")


class Inspection(models.Model):
    return_line = models.ForeignKey(
        ReturnLine,
        on_delete=models.CASCADE,
        related_name="inspections"
    )
    inspected_date = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=30)
    notes = models.TextField(blank=True)
    inspected_by = models.CharField(max_length=100, blank=True)


class Refund(models.Model):
    refund_id = models.CharField(max_length=30, unique=True)
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name="refunds"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    refund_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="PENDING")
    transaction_reference = models.CharField(max_length=100, blank=True)

class InventoryDisposition(models.Model):
    return_line = models.ForeignKey(
        ReturnLine,
        on_delete=models.CASCADE,
        related_name="dispositions"
    )
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    disposition_type = models.CharField(max_length=30)
    quantity = models.PositiveIntegerField()
    processed_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

class ReturnEvent(models.Model):
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name="events"
    )
    event_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    actor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class GroundTruth(models.Model):
    return_request = models.ForeignKey(
        ReturnRequest,
        on_delete=models.CASCADE,
        related_name="ground_truth_labels"
    )

    issue_type = models.CharField(max_length=100)

    expected_decision = models.CharField(max_length=100)

    details = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.return_request.return_id} - "
            f"{self.issue_type}"
        )