
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from returns.models import (
    ReturnRequest,
    Refund,
    InventoryDisposition,
    GroundTruth,
)


class Command(BaseCommand):
    help = "Generate labelled ReturnFlow edge cases"

    @transaction.atomic
    def handle(self, *args, **options):

        requests = list(
            ReturnRequest.objects.order_by("return_id")[:5]
        )

        if len(requests) < 5:
            raise CommandError("At least 5 return requests are required.")

        for request in requests:
            if not request.return_lines.exists():
                raise CommandError(
                    f"{request.return_id} has no return lines."
                )

        # Case 1: Return quantity exceeds purchased quantity
        request = requests[0]
        line = request.return_lines.first()

        line.quantity = line.order_line.quantity + 1
        line.save(update_fields=["quantity"])

        self.add_label(
            request,
            "EXCESS_RETURN_QUANTITY",
            "REJECT_EXCESS_QUANTITY",
            "Return quantity exceeds purchased quantity."
        )

        # Case 2: Refund exceeds the recorded order total
        request = requests[1]

        Refund.objects.get_or_create(
            refund_id=f"RDP-{request.return_id[-10:]}",
            defaults={
                "return_request": request,
                "amount": request.order.total_amount + Decimal("1.00"),
                "status": "BLOCKED",
                "transaction_reference": "EXCESS-REFUND-ATTEMPT",
            }
        )

        self.add_label(
            request,
            "EXCESS_REFUND",
            "BLOCK_REFUND",
            "Refund amount exceeds the recorded order total."
        )

        # Case 3: Restock before inspection
        request = requests[2]
        line = request.return_lines.first()
        inspection = line.inspections.first()

        if not inspection:
            raise CommandError(
                f"No inspection exists for {request.return_id}."
            )

        note = "EDGE_CASE: Restock attempted before inspection."

        disposition = InventoryDisposition.objects.filter(
            return_line=line,
            notes=note
        ).first()

        if not disposition:
            disposition = InventoryDisposition.objects.create(
                return_line=line,
                inspection=None,
                disposition_type="RESTOCK",
                quantity=line.quantity,
                notes=note
            )

        InventoryDisposition.objects.filter(
            pk=disposition.pk
        ).update(
            processed_date=inspection.inspected_date - timedelta(days=1)
        )

        self.add_label(
            request,
            "RESTOCK_BEFORE_INSPECTION",
            "BLOCK_RESTOCK",
            "Restock record occurs before inspection."
        )

        # Case 4: Return requested after the assumed 30-day window
        request = requests[3]

        late_date = request.order.order_date + timedelta(days=31)

        ReturnRequest.objects.filter(pk=request.pk).update(
            request_date=late_date
        )

        self.add_label(
            request,
            "LATE_RETURN",
            "REJECT_WITHOUT_OVERRIDE",
            "Return requested 31 days after order date; assumed policy is 30 days."
        )

        # Case 5: Duplicate refund attempt
        request = requests[4]

        original_refund = request.refunds.order_by("refund_id").first()

        if not original_refund:
            raise CommandError(
                f"No original refund exists for {request.return_id}."
            )

        Refund.objects.get_or_create(
            refund_id=f"REF-EDGE-DUP-{request.return_id}",
            defaults={
                "return_request": request,
                "amount": original_refund.amount,
                "refund_date": original_refund.refund_date,
                "status": "BLOCKED_DUPLICATE",
                "transaction_reference": "DUPLICATE-REFUND-ATTEMPT"
            }
        )

        self.add_label(
            request,
            "DUPLICATE_REFUND",
            "BLOCK_DUPLICATE_PAYOUT",
            "A second refund was attempted and marked as blocked."
        )

        self.stdout.write(
            self.style.SUCCESS("Five labelled edge cases created.")
        )

    def add_label(self, request, issue, decision, details):

        GroundTruth.objects.update_or_create(
            return_request=request,
            issue_type=issue,
            defaults={
                "expected_decision": decision,
                "details": details
            }
        )
