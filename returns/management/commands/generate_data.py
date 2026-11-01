
import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from returns.models import (
    Customer,
    Order,
    OrderLine,
    ReturnRequest,
    ReturnLine,
    ReturnAuthorization,
    ReturnShipment,
    Inspection,
    Refund,
    InventoryDisposition,
    ReturnEvent,
)


class Command(BaseCommand):

    help = "Generate synthetic data for ReverseFlow"

    def add_arguments(self, parser):

        parser.add_argument("--seed", type=int, default=20261022)
        parser.add_argument("--customers", type=int, default=5000)
        parser.add_argument("--orders", type=int, default=30000)
        parser.add_argument("--returns", type=int, default=5000)
        parser.add_argument("--return-lines", type=int, default=8000)

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing customer-related data first"
        )

    def handle(self, *args, **options):

        rng = random.Random(options["seed"])

        customer_count = options["customers"]
        order_count = options["orders"]
        return_count = options["returns"]
        return_line_count = options["return_lines"]

        # Step 1: Validate input

        if min(customer_count, order_count, return_count) < 1:
            raise CommandError("Counts must be greater than zero.")

        if order_count < return_count:
            raise CommandError(
                "Orders must be at least equal to return requests."
            )

        if return_line_count < return_count:
            raise CommandError(
                "Return lines must be at least equal to return requests."
            )

        if return_line_count > return_count * 2:
            raise CommandError(
                "Maximum two return lines per request are supported."
            )

        # Step 2: Check existing records

        if options["clear"]:
            Customer.objects.all().delete()

        elif (
            Customer.objects.exists()
            or Order.objects.exists()
            or ReturnRequest.objects.exists()
        ):
            raise CommandError(
                "Database already contains data. "
                "Use --clear to generate fresh data."
            )

        self.stdout.write("Starting ReverseFlow data generation...")

        with transaction.atomic():

            # Step 3: Generate customers

            customers = []

            for i in range(1, customer_count + 1):

                customers.append(
                    Customer(
                        customer_id=f"CUS-2026-{i:06d}",
                        name=f"Customer {i}",
                        email=f"customer{i}@example.com",
                        phone=f"9{rng.randint(100000000, 999999999)}"
                    )
                )

            Customer.objects.bulk_create(
                customers,
                batch_size=1000
            )

            customers = list(
                Customer.objects.order_by("customer_id")
            )

            self.stdout.write("Customers created.")

            # Step 4: Generate orders

            products = [
                ("Laptop", Decimal("50000.00")),
                ("Mobile", Decimal("20000.00")),
                ("Headphones", Decimal("2500.00")),
                ("Keyboard", Decimal("1500.00")),
                ("Monitor", Decimal("12000.00")),
            ]

            statuses = ["PLACED", "SHIPPED", "DELIVERED"]

            return_order_numbers = set(
                rng.sample(range(1, order_count + 1), return_count)
            )

            base_date = timezone.make_aware(
                datetime(2026, 1, 1)
            )

            orders = []

            for i in range(1, order_count + 1):

                order_date = base_date + timedelta(
                    days=rng.randint(0, 300)
                )

                status = (
                    "DELIVERED"
                    if i in return_order_numbers
                    else rng.choice(statuses)
                )

                orders.append(
                    Order(
                        order_id=f"ORD-2026-{i:06d}",
                        customer=rng.choice(customers),
                        order_date=order_date,
                        total_amount=Decimal("0.00"),
                        status=status
                    )
                )

            Order.objects.bulk_create(
                orders,
                batch_size=1000
            )

            orders = list(
                Order.objects.order_by("order_id")
            )

            order_by_id = {
                order.order_id: order
                for order in orders
            }

            self.stdout.write("Orders created.")

            # Step 5: Generate order lines

            order_lines = []

            for order in orders:

                total = Decimal("0.00")

                selected_products = rng.sample(products, 2)

                for product_name, price in selected_products:

                    quantity = rng.randint(1, 3)

                    order_lines.append(
                        OrderLine(
                            order=order,
                            product_name=product_name,
                            quantity=quantity,
                            unit_price=price
                        )
                    )

                    total += price * quantity

                order.total_amount = total

            OrderLine.objects.bulk_create(
                order_lines,
                batch_size=1000
            )

            Order.objects.bulk_update(
                orders,
                ["total_amount"],
                batch_size=1000
            )

            order_lines = list(
                OrderLine.objects.select_related("order").all()
            )

            lines_by_order = {}

            for line in order_lines:
                lines_by_order.setdefault(
                    line.order_id, []
                ).append(line)

            self.stdout.write("Order lines created.")

            # Step 6: Generate return requests

            selected_return_orders = sorted(
                return_order_numbers
            )

            return_requests = []

            for i, order_number in enumerate(
                selected_return_orders, start=1
            ):

                order = order_by_id[
                    f"ORD-2026-{order_number:06d}"
                ]

                return_requests.append(
                    ReturnRequest(
                        return_id=f"RMA-2026-{i:06d}",
                        order=order,
                        reason=rng.choice([
                            "Product damaged",
                            "Wrong product delivered",
                            "Product defective",
                            "Product not as expected",
                            "Late delivery"
                        ]),
                        status="REQUESTED"
                    )
                )

            ReturnRequest.objects.bulk_create(
                return_requests,
                batch_size=1000
            )

            return_requests = list(
                ReturnRequest.objects.select_related(
                    "order"
                ).order_by("return_id")
            )

            self.stdout.write("Return requests created.")

            # Step 7: Generate return lines

            extra_lines = return_line_count - return_count

            two_line_requests = set(
                rng.sample(
                    range(return_count),
                    extra_lines
                )
            )

            return_lines = []

            for index, request in enumerate(return_requests):

                available_lines = lines_by_order[
                    request.order_id
                ]

                number_of_lines = (
                    2 if index in two_line_requests else 1
                )

                selected_lines = rng.sample(
                    available_lines,
                    number_of_lines
                )

                for order_line in selected_lines:

                    return_lines.append(
                        ReturnLine(
                            return_request=request,
                            order_line=order_line,
                            quantity=rng.randint(
                                1,
                                order_line.quantity
                            )
                        )
                    )

            ReturnLine.objects.bulk_create(
                return_lines,
                batch_size=1000
            )

            return_lines = list(
                ReturnLine.objects.select_related(
                    "return_request",
                    "order_line"
                ).all()
            )

            self.stdout.write("Return lines created.")

            # Step 8: Generate authorizations

            authorizations = []

            for i, request in enumerate(
                return_requests, start=1
            ):

                authorization_date = (
                    request.request_date + timedelta(days=1)
                )

                authorizations.append(
                    ReturnAuthorization(
                        authorization_id=f"AUTH-2026-{i:06d}",
                        return_request=request,
                        approved=True,
                        authorized_date=authorization_date,
                        status="APPROVED"
                    )
                )

            ReturnAuthorization.objects.bulk_create(
                authorizations,
                batch_size=1000
            )

            authorizations = list(
                ReturnAuthorization.objects.select_related(
                    "return_request"
                ).order_by("authorization_id")
            )

            self.stdout.write("Authorizations created.")

            # Step 9: Generate return shipments

            shipments = []

            for i, authorization in enumerate(
                authorizations, start=1
            ):

                shipped_date = (
                    authorization.authorized_date + timedelta(days=2)
                )

                received_date = shipped_date + timedelta(days=3)

                shipments.append(
                    ReturnShipment(
                        shipment_id=f"RTS-2026-{i:06d}",
                        authorization=authorization,
                        tracking_number=f"TRACK-{i:08d}",
                        shipped_date=shipped_date,
                        received_date=received_date,
                        status="RECEIVED"
                    )
                )

            ReturnShipment.objects.bulk_create(
                shipments,
                batch_size=1000
            )

            self.stdout.write("Shipments created.")

            # Step 10: Generate inspections

            inspections = []

            for i, line in enumerate(return_lines, start=1):

                condition = rng.choice([
                    "GOOD",
                    "DAMAGED",
                    "DEFECTIVE"
                ])

                inspections.append(
                    Inspection(
                        return_line=line,
                        condition=condition,
                        notes=f"Inspection completed for return line {i}.",
                        inspected_by="Warehouse Operator"
                    )
                )

            Inspection.objects.bulk_create(
                inspections,
                batch_size=1000
            )

            inspections = list(
                Inspection.objects.select_related(
                    "return_line"
                ).order_by("id")
            )

            self.stdout.write("Inspections created.")

            # Step 11: Generate inventory dispositions

            dispositions = []

            for inspection in inspections:

                if inspection.condition in ["DAMAGED", "DEFECTIVE"]:
                    disposition_type = "QUARANTINE"
                else:
                    disposition_type = "RESTOCK"

                dispositions.append(
                    InventoryDisposition(
                        return_line=inspection.return_line,
                        inspection=inspection,
                        disposition_type=disposition_type,
                        quantity=inspection.return_line.quantity,
                        notes="Disposition based on inspection result."
                    )
                )

            InventoryDisposition.objects.bulk_create(
                dispositions,
                batch_size=1000
            )

            self.stdout.write("Inventory dispositions created.")

            # Step 12: Generate refunds

            refund_amounts = {}

            for line in return_lines:

                request_id = line.return_request_id

                amount = (
                    line.unit_price
                    if hasattr(line, "unit_price")
                    else line.order_line.unit_price
                ) * line.quantity

                refund_amounts[request_id] = (
                    refund_amounts.get(
                        request_id,
                        Decimal("0.00")
                    ) + amount
                )

            refunds = []

            for i, request in enumerate(
                return_requests, start=1
            ):

                refunds.append(
                    Refund(
                        refund_id=f"REF-2026-{i:06d}",
                        return_request=request,
                        amount=refund_amounts[request.pk],
                        refund_date=(
                            request.order.order_date
                            + timedelta(days=15)
                        ),
                        status="PROCESSED",
                        transaction_reference=f"TXN-{i:08d}"
                    )
                )

            Refund.objects.bulk_create(
                refunds,
                batch_size=1000
            )

            self.stdout.write("Refunds created.")

            # Step 13: Generate return events

            events = []

            for request in return_requests:

                events.append(
                    ReturnEvent(
                        return_request=request,
                        event_type="RETURN_COMPLETED",
                        description=(
                            "Return authorized, shipped, inspected, "
                            "disposition recorded and refund processed."
                        ),
                        actor="Operations Manager"
                    )
                )

                request.status = "COMPLETED"

            ReturnEvent.objects.bulk_create(
                events,
                batch_size=1000
            )

            ReturnRequest.objects.bulk_update(
                return_requests,
                ["status"],
                batch_size=1000
            )

            self.stdout.write("Return events created.")

        # Step 14: Display final counts

        self.stdout.write(
            self.style.SUCCESS(
                "\nReverseFlow data generation completed!"
            )
        )

        self.stdout.write(
            f"Customers: {Customer.objects.count()}"
        )

        self.stdout.write(
            f"Orders: {Order.objects.count()}"
        )

        self.stdout.write(
            f"Order Lines: {OrderLine.objects.count()}"
        )

        self.stdout.write(
            f"Return Requests: {ReturnRequest.objects.count()}"
        )

        self.stdout.write(
            f"Return Lines: {ReturnLine.objects.count()}"
        )

        self.stdout.write(
            f"Authorizations: {ReturnAuthorization.objects.count()}"
        )

        self.stdout.write(
            f"Shipments: {ReturnShipment.objects.count()}"
        )

        self.stdout.write(
            f"Inspections: {Inspection.objects.count()}"
        )

        self.stdout.write(
            f"Dispositions: {InventoryDisposition.objects.count()}"
        )

        self.stdout.write(
            f"Refunds: {Refund.objects.count()}"
        )

        self.stdout.write(
            f"Return Events: {ReturnEvent.objects.count()}"
        )
