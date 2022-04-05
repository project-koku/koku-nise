#
# Copyright 2022 Red Hat, Inc.
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
"""Defines the abstract generator."""
import datetime
from copy import deepcopy
from random import choice
from random import choices
from random import randint
from random import uniform
from string import ascii_lowercase
from abc import abstractmethod
from faker import Faker

from dateutil import parser
from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE


OCI_COST_REPORT="oci_cost_report"
OCI_USAGE_REPORT = "oci_usage_report"

OCI_IDENTITY_COLUMNS=(
    "lineItem/referenceNo",
    "lineItem/tenantId",
    "lineItem/intervalUsageStart",
    "lineItem/intervalUsageEnd",
    "product/service"
)
OCI_USAGE_PRODUCT_COLS = {
    "product/resource"
}
OCI_COMMON_PRODUCT_COLS = (
    "product/compartmentId",
    "product/compartmentName",
    "product/region",
    "product/availabilityDomain",
    "product/resourceId",
)
OCI_COST_COLUMNS = (
    "usage/billedQuantity",
    "usage/billedQuantityOverage",
    "cost/subscriptionId",
    "cost/productSku",
    "product/Description",
    "cost/unitPrice",
    "cost/unitPriceOverage",
    "cost/myCost",
    "cost/myCostOverage",
    "cost/currencyCode",
    "cost/billingUnitReadable",
    "cost/skuUnitDescription",
    "cost/overageFlag",
)
OCI_USAGE_COLUMNS = (
    "usage/consumedQuantity",
    "usage/billedQuantity",
    "usage/consumedQuantityUnits",
    "usage/consumedQuantityMeasure"
)
OCI_CORRECTION_COLUMNS=(
    "lineItem/isCorrection",
    "lineItem/backreferenceNo"
)
OCI_TAGS_COLUMNS=(
    "tags/Oracle-Tags.CreatedBy",
    "tags/Oracle-Tags.CreatedOn",
    "tags/orcl-cloud.free-tier-retained",
)
OCI_ALL_COMMON_COLUMNS = (
    OCI_IDENTITY_COLUMNS
    + OCI_COMMON_PRODUCT_COLS
    + OCI_CORRECTION_COLUMNS
    + OCI_TAGS_COLUMNS
)

OCI_REPORT_TYPE_TO_COLS = {
    OCI_COST_REPORT: (
        OCI_IDENTITY_COLUMNS
        + OCI_COMMON_PRODUCT_COLS
        + OCI_COST_COLUMNS
        + OCI_CORRECTION_COLUMNS
        + OCI_TAGS_COLUMNS
    ),
    OCI_USAGE_REPORT: (
        OCI_IDENTITY_COLUMNS
        + tuple(OCI_USAGE_PRODUCT_COLS)
        + OCI_COMMON_PRODUCT_COLS
        + OCI_USAGE_COLUMNS
        + OCI_CORRECTION_COLUMNS
        + OCI_TAGS_COLUMNS
    )
}

class OCIGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    OCI_REGIONS_TO_DOMAIN = [
        {"region": "ap-sydney-1", "domain":1},
        {"region": "ap-melbourne-1", "domain":1},
        {"region": "sa-saopaulo-1",	"domain":1},
        {"region": "sa-vinhedo-1", "domain": 1},
        {"region": "ca-montreal-1", "domain": 1},
        {"region": "ca-toronto-1", "domain": 1},
        {"region": "sa-santiago-1", "domain": 1},
        {"region": "eu-marseille-1", "domain": 1},
        {"region": "eu-frankfurt-1", "domain": 3},
        {"region": "ap-hyderabad-1", "domain": 1},
        {"region": "ap-mumbai-1", "domain": 1},
        {"region": "il-jerusalem-1", "domain": 1},
        {"region": "eu-milan-1", "domain": 1},
        {"region": "ap-osaka-1", "domain": 1},
        {"region": "ap-tokyo-1", "domain": 1},
        {"region": "eu-amsterdam-1", "domain": 1},
        {"region": "me-jeddah-1", "domain": 1},
        {"region": "ap-singapore-1", "domain": 1},
        {"region": "af-johannesburg-1", "domain": 1},
        {"region": "ap-seoul-1", "domain": 1},
        {"region": "ap-chuncheon-1", "domain": 1},
        {"region": "eu-stockholm-1", "domain": 1},
        {"region": "eu-zurich-1", "domain": 1},
        {"region": "me-abudhabi-1", "domain": 1},
        {"region": "me-dubai-1", "domain": 1},
        {"region": "uk-london-1", "domain": 1},
        {"region": "uk-cardiff-1",	"domain": 1},
        {"region": "us-ashburn-1",	"domain": 3},
        {"region": "us-phoenix-1", "domain": 3},	
        {"region": "us-sanjose-1", "domain": 1}
    ]
    fake = Faker()

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the generator."""
        super().__init__(start_date, end_date)
        self.currency = currency
        # TODO: to be modified/organized
        self.tenant_id = f"ocid1.tenancy.oc1..{self.fake.pystr(min_chars=20, max_chars=50)}"
        self.reference_no = self._get_reference_num()
        self.compartment_id = self.tenant_id
        self.compartment_name = self.fake.name().replace(' ', '').lower()
        self.region_to_domain = choice(self.OCI_REGIONS_TO_DOMAIN)
        self.product_region = self._get_product_region()
        self.availability_domain = self._get_availability_domain()
        self.is_correction = choice(["true", "false"])
        self.email_domain = self.fake.free_email_domain()
        self.subscription_id = self.fake.random_number(fix_len=True, digits=8)

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%MZ")

    def _init_data_row(self, start, end, **kwargs):
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        report_type = kwargs.get(REPORT_TYPE)
        row = {}
        for column in OCI_REPORT_TYPE_TO_COLS[report_type]:
            row[column] = ""
        return row

    def _add_common_usage_info(self, row, start, end):
        """Add common usage information."""
        data = self._get_common_usage_data(start, end)
        for column in OCI_ALL_COMMON_COLUMNS:
            row[column] = data[column]
        return row   

    def _get_common_usage_data(self,start, end):
        """Generate data for common columns."""

        data = {
            "lineItem/referenceNo": f"{self.reference_no}+{self.fake.pystr()}==",
            "lineItem/tenantId": self.tenant_id,
            "lineItem/intervalUsageStart": OCIGenerator.timestamp(start),
            "lineItem/intervalUsageEnd": OCIGenerator.timestamp(end),
            "product/service":"",
            "product/compartmentId": self.compartment_id,
            "product/compartmentName": self.compartment_name,
            "product/region": self.product_region,
            "product/availabilityDomain": self.availability_domain,
            "product/resourceId":"",
            "lineItem/isCorrection": self.is_correction,
            "lineItem/backreferenceNo": f"{self.reference_no}+{self.fake.pystr()}==" if self.is_correction == "true" else "",
            "tags/Oracle-Tags.CreatedBy": f"default/{self.compartment_name}@{self.email_domain}",
            "tags/Oracle-Tags.CreatedOn": choice([self._tag_timestamp(start), self._tag_timestamp(end), ""]),
            "tags/orcl-cloud.free-tier-retained": choice(["true", ""]),
        }
        return data

    def _get_reference_num(self):
        """Get reference number"""
        ref_num = f"V2.{self.fake.pystr(min_chars=20, max_chars=50)}"
        return ref_num

    def _tag_timestamp(self, in_date):
        """Provide timestamp a tag date."""
        tag_date = ""
        if (in_date and isinstance(in_date, datetime.datetime)):
            _date = in_date + datetime.timedelta(minutes=randint(1, 50), seconds=randint(1, 50))
            tag_date = _date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return tag_date
    
    def _get_product_region(self):
        """Get a random region""" 
        return self.region_to_domain.get('region')

    def _get_availability_domain(self):
        """Get availability domain of the region"""
        a_domain = f"{self.fake.pystr(max_chars=4)}:{self.product_region.upper()}-AD-{self.region_to_domain.get('domain')}"
        return a_domain

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific info."""

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end, **kwargs)
            row = self._add_common_usage_info(row, start, end)
            row = self._update_data(row, start, end, **kwargs)
            yield row
    
    @abstractmethod
    def generate_data(self, report_type=None, **kwargs):
        """Responsibile for generating data."""