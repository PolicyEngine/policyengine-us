from policyengine_us.model_api import *


class HILIHEAPPhotovoltaicStatus(Enum):
    NO_PV = "No photovoltaic system"
    PV_WITH_NET_USAGE = "Photovoltaic system with net billed electricity usage"
    PV_WITHOUT_NET_USAGE = "Photovoltaic system without net billed electricity usage"


class hi_liheap_photovoltaic_status(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HILIHEAPPhotovoltaicStatus
    # Apply ordinary dwelling rules when this input is omitted.
    default_value = HILIHEAPPhotovoltaicStatus.NO_PV
    # Report net billed electricity use over the utility's one-year billing cycle.
    definition_period = YEAR
    label = "Hawaii LIHEAP photovoltaic status"
    reference = (
        # Draft FY2026 manual 2.12, 4.2 and 6.2.
        # PDF pages 61,65,69
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=61",
    )
