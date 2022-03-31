from nise.generators.oci.oci_generator import OCIGenerator
from nise.generators.oci.oci_generator import OCI_COST_REPORT
from nise.generators.oci.oci_generator import OCI_USAGE_REPORT
from nise.generators.oci.oci_generator import OCI_COST_COLUMNS
from nise.generators.oci.oci_generator import OCI_USAGE_COLUMNS
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS


SERVICE = "NETWORK"

class OCINetworkGenerator(OCIGenerator):
    """Generator for OCI Network data."""

    def __init__(self, start_date, end_date, currency, report_type, attributes=None):
        """Initialize the network generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.report_type = report_type
        self.service = SERVICE

    def _update_data(self, row, start, end, **kwargs):
        """Update a data row with network values."""
        row["product/service"] = self.service
        return row

    def generate_data(self, report_type=None, **kwargs):
        """Generate OCI network data."""
        if report_type:
            kwargs.update({"report_type":report_type})
        return self._generate_hourly_data(**kwargs)
