from policyengine_us.model_api import *


class ri_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.RI
    documentation = (
        "Rhode Island other modifications decreasing federal adjusted gross income "
        "reported on Schedule M, entered as a positive amount, excluding subtractions "
        "PolicyEngine calculates separately."
    )
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2026-01/2025%20RI%20Schedule%20M_w.pdf#page=1"
