#
# Copyright 2021 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Module for gcp database data generation."""
from datetime import datetime
from random import choice
from random import uniform

from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS_JSONL
from nise.generators.gcp.gcp_generator import GCPGenerator


class GCPDatabaseGenerator(GCPGenerator):
    """Generator for GCP Database data."""

    # Service Description and Service ID
    SERVICE = (
        ("SQL", "66AB-BA17-351C"),
        ("Spanner", "S3LS-JE3X-DR2Z"),
        ("Bigtable", "SLKD-3XKD-34SX-AL3C"),
        ("Firestore", "SLW3-CNSL-23SD"),
        ("Firebase" , "SLK2-CJ23-823X"),
        ("Memorystore", "DJW3-482X-DHEC"),
        ("MongoDB", "2XL2-DJ23-ZL3S"),
    )

    # (ID, Description, Usage Unit, Pricing Unit)
    SKU = (
        ("66AB-BA17-351C", "Storage PD Snapshot", "byte-seconds", "gibibyte month"),
    )

    LABELS = (("[{'key': 'vm_key_proj2', 'value': 'vm_label_proj2'}]"), ("[]"))

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        service = choice(self.SERVICE)
        sku = choice(self.SKU)
        row["system_labels"] = "[]"
        row["service.description"] = service[0]
        row["service.id"] = service[1]
        row["sku.id"] = sku[0]
        row["sku.description"] = sku[1]
        usage_unit = sku[2]
        pricing_unit = sku[3]
        row["usage.unit"] = usage_unit
        row["usage.pricing_unit"] = pricing_unit
        row["labels"] = choice(self.LABELS)
        row["credits"] = "[]"
        row["cost_type"] = "regular"
        row["currency"] = "USD"
        row["currency_conversion_rate"] = 1
        if self.attributes and self.attributes.get("usage.amount"):
            row["usage.amount"] = self.attributes.get("usage.amount")
        else:
            row["usage.amount"] = self._gen_usage_unit_amount(usage_unit)
        if self.attributes and self.attributes.get("usage.amount_in_pricing_units"):
            row["usage.amount_in_pricing_units"] = self.attributes.get("usage.amount_in_pricing_units")
        else:
            row["usage.amount_in_pricing_units"] = self._gen_pricing_unit_amount(pricing_unit, row["usage.amount"])
        if self.attributes and self.attributes.get("price"):
            row["cost"] = row["usage.amount_in_pricing_units"] * self.attributes.get("price")
        else:
            row["cost"] = round(uniform(0, 0.01), 7)
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        row["invoice.month"] = f"{usage_date.year}{usage_date.month:02d}"
        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()
