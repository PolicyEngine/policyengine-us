from policyengine_us.model_api import *


class hi_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    documentation = (
        "Hawaii other subtractions from federal adjusted gross income reported on "
        "Form N-11, Line 18 (Other subtractions), entered as a positive amount. "
        "Do not include pension income, Social Security, military pay exclusions, "
        "U.S. government interest, or student loan interest deductions, "
        "which PolicyEngine computes separately."
    )
    reference = "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=14"
