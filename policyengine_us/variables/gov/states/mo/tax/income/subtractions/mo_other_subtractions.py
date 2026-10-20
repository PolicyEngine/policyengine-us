from policyengine_us.model_api import *


class mo_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Missouri other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO
    documentation = (
        "Missouri other subtractions from federal adjusted gross income reported on "
        "Form MO-A, Part 1, Line 18 (Other subtractions), entered as a positive amount. "
        "Do not include health insurance premiums, U.S. government interest, 529 deductions, "
        "capital gains subtractions, or state tax refunds, which PolicyEngine computes separately."
    )
    reference = "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=13"
