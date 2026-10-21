from policyengine_us.model_api import *


class foreign_housing_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign housing exclusion under section 911(a)(2)"
    unit = USD
    documentation = "Housing amount excluded under 26 U.S.C. 911(a)(2): Form 2555 line 36, summed across both spouses on a joint return. This is separate from the line 50 housing deduction."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911#a_2",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
