from policyengine_us.model_api import *


class has_cooling_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has cooling costs"
    documentation = "Whether the household incurs air-conditioning or other cooling costs separately from its rent or mortgage. Cooling is not derivable from the electricity bill, so it is its own fact; it qualifies the household for the SNAP heating and cooling standard utility allowance."
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(d)(6)(iii)(D)(1)"
    )
