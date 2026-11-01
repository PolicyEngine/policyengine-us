from policyengine_us.model_api import *


class nc_lieap_has_paid_excess_heating_costs(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Paid excess heating charges for North Carolina LIEAP"
    documentation = (
        "Whether the household paid excess heating-utility charges in the "
        "12 months before application at its current address. This is the "
        "public-housing exception when heating utilities are included in rent "
        "under EP-300.08(4). An unpaid charge or a payment at a previous address "
        "does not meet this condition."
    )
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=9"
    )
