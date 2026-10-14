from policyengine_us.model_api import *


class foreign_earned_income_exclusion_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign earned income exclusion under section 911(a)(1)"
    unit = USD
    documentation = "Foreign earned income excluded under 26 U.S.C. 911(a)(1): Form 2555 line 42, summed across both spouses on a joint return. This excludes the line 36 housing exclusion and the line 50 housing deduction."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911#a_1",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
