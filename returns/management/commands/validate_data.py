
from collections import defaultdict

from django.core.management.base import BaseCommand

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
    GroundTruth,
)


class Command(BaseCommand):
    help = "Validate ReturnFlow database records"

    def handle(self, *args, **options):
        errors = 0
        warnings = 0
        expected_anomalies = 0

        def error(message):
            nonlocal errors
            errors += 1
            self.stdout.write(self.style.ERROR(f"ERROR: {message}"))

        def warning(message):
            nonlocal warnings
            warnings += 1
            self.stdout.write(self.style.WARNING(f"WARNING: {message}"))

        def expected(message):
            nonlocal expected_anomalies
            expected_anomalies += 1
            self.stdout.write(
                self.style.WARNING(f"EXPECTED ANOMALY: {message}")
            )

        self.stdout.write("Starting ReturnFlow validation...\n")

        models = [
            Customer, Order, OrderLine, ReturnRequest, ReturnLine,
            ReturnAuthorization, ReturnShipment, Inspection, Refund,
            InventoryDisposition, ReturnEvent,
        ]

        # 1. Record counts and primary-key checks
        for model in models:
            count = model.objects.count()
            self.stdout.write(f"{model.__name__}: {count} records")

            if model.objects.values("pk").distinct().count() != count:
                error(f"Duplicate primary keys in {model.__name__}")

        # 2. Foreign-key checks
        relations = [
            (Order, "customer"),
            (OrderLine, "order"),
            (ReturnRequest, "order"),
            (ReturnLine, "return_request"),
            (ReturnLine, "order_line"),
            (ReturnAuthorization, "return_request"),
            (ReturnShipment, "authorization"),
            (Inspection, "return_line"),
            (Refund, "return_request"),
            (InventoryDisposition, "return_line"),
            (ReturnEvent, "return_request"),
        ]

        for model, field_name in relations:
            fk_field = model._meta.get_field(field_name)
            related_model = fk_field.related_model

            invalid_count = (
                model.objects
                .exclude(**{
                    f"{field_name}__in": related_model.objects.values("pk")
                })
                .count()
            )

            if invalid_count:
                error(
                    f"{model.__name__}.{field_name}: "
                    f"{invalid_count} invalid relationships"
                )

        # 3. Return quantity checks
        returned_quantities = defaultdict(int)

        for line in ReturnLine.objects.select_related(
            "order_line", "return_request"
        ).iterator():

            if line.quantity <= 0:
                error(f"Non-positive return quantity in ReturnLine {line.pk}")
                continue

            returned_quantities[line.order_line_id] += line.quantity

        for order_line_id, returned_qty in returned_quantities.items():
            order_line = OrderLine.objects.get(pk=order_line_id)
            purchased_qty = order_line.quantity

            if returned_qty > purchased_qty:
                labelled = GroundTruth.objects.filter(
                    return_request__return_lines__order_line_id=order_line_id,
                    issue_type="EXCESS_RETURN_QUANTITY",
                ).exists()

                if labelled:
                    expected(
                        f"OrderLine {order_line_id}: returned {returned_qty}, "
                        f"purchased {purchased_qty}"
                    )
                else:
                    error(
                        f"OrderLine {order_line_id}: returned {returned_qty}, "
                        f"purchased {purchased_qty}"
                    )

        # 4. Refund amount checks
        for refund in Refund.objects.select_related(
            "return_request"
        ).iterator():

            expected_amount = sum(
                (
                    line.order_line.unit_price * line.quantity
                    for line in refund.return_request.return_lines.select_related(
                        "order_line"
                    ).all()
                ),
                start=0,
            )

            if refund.amount != expected_amount:
                labelled = GroundTruth.objects.filter(
                    return_request=refund.return_request,
                    issue_type__in=[
                        "EXCESS_REFUND",
                        "DUPLICATE_REFUND",
                        "EXCESS_RETURN_QUANTITY",
                    ],
                ).exists()

                if labelled:
                    expected(
                        f"Refund amount mismatch: {refund.refund_id}"
                    )
                else:
                    error(f"Refund amount mismatch: {refund.refund_id}")

        # 5. Authorization dates
        for authorization in ReturnAuthorization.objects.select_related(
            "return_request__order"
        ).iterator():

            if authorization.authorized_date:
                if authorization.authorized_date < (
                    authorization.return_request.request_date
                ):
                    error(
                        f"Authorization date before request date: "
                        f"{authorization.authorization_id}"
                    )

        # 6. Shipment dates
        for shipment in ReturnShipment.objects.iterator():

            if (
                shipment.shipped_date
                and shipment.received_date
                and shipment.received_date < shipment.shipped_date
            ):
                error(f"Shipment date order invalid: {shipment.shipment_id}")

        # 7. Inspection and disposition checks
        for disposition in InventoryDisposition.objects.select_related(
            "inspection", "return_line"
        ).iterator():

            if disposition.quantity <= 0:
                error(f"Invalid disposition quantity: {disposition.pk}")

            if (
                disposition.inspection
                and disposition.inspection.return_line_id
                != disposition.return_line_id
            ):
                error(f"Disposition inspection mismatch: {disposition.pk}")

            if (
                disposition.disposition_type == "RESTOCK"
                and disposition.inspection is None
                and disposition.notes.startswith("EDGE_CASE:")
            ):
                labelled = GroundTruth.objects.filter(
                    return_request=disposition.return_line.return_request,
                    issue_type="RESTOCK_BEFORE_INSPECTION",
                ).exists()

                if labelled:
                    expected(
                        f"Restock before inspection: {disposition.pk}"
                    )
                else:
                    error(
                        f"Restock before inspection: {disposition.pk}"
                    )

        # 8. Final report
        self.stdout.write("\n--- VALIDATION SUMMARY ---")
        self.stdout.write(f"Errors: {errors}")
        self.stdout.write(f"Warnings: {warnings}")
        self.stdout.write(f"Expected anomalies: {expected_anomalies}")

        if errors == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Validation completed with no unexpected errors."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Validation failed. Fix unexpected errors."
                )
            )
