
import csv
import json

from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

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

    help = "Export ReverseFlow database records to CSV and JSON"

    def add_arguments(self, parser):

        parser.add_argument(
            "--format",
            choices=["csv", "json", "both"],
            default="both",
            help="Choose CSV, JSON or both formats"
        )

    def handle(self, *args, **options):

        export_format = options["format"]

        # Create exports folder

        export_folder = Path(settings.BASE_DIR) / "exports"
        export_folder.mkdir(parents=True, exist_ok=True)

        models = [
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
        ]

        for model in models:

            model_name = model.__name__.lower()

            fields = [
                field.attname
                for field in model._meta.concrete_fields
            ]

            records = []

            for obj in model.objects.all().iterator():

                record = {
                    field: getattr(obj, field)
                    for field in fields
                }

                records.append(record)

            # Export CSV

            if export_format in ["csv", "both"]:

                csv_path = export_folder / f"{model_name}.csv"

                with open(
                    csv_path,
                    "w",
                    newline="",
                    encoding="utf-8"
                ) as file:

                    writer = csv.DictWriter(
                        file,
                        fieldnames=fields
                    )

                    writer.writeheader()
                    writer.writerows(records)

                self.stdout.write(
                    f"CSV exported: {csv_path.name}"
                )

            # Export JSON

            if export_format in ["json", "both"]:

                json_path = export_folder / f"{model_name}.json"

                with open(
                    json_path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        records,
                        file,
                        indent=4,
                        default=str
                    )

                self.stdout.write(
                    f"JSON exported: {json_path.name}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "All exports completed successfully!"
            )
        )
