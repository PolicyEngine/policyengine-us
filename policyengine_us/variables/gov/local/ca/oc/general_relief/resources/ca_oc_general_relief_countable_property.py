from policyengine_us.model_api import *


class ca_oc_general_relief_countable_property(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable property"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=01"
    # Countable personal property under the $1,000 limit (Sec 60.2.a): liquid
    # resources (cash) plus the value of any non-excluded vehicle. We don't track
    # non-vehicle personal property or real estate, which partners do not collect.
    adds = [
        "spm_unit_cash_assets",
        "ca_oc_general_relief_countable_vehicle_value",
    ]
