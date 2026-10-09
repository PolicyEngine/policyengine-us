from policyengine_us.model_api import *


class foreign_earned_income_exclusion_gross(Variable):
    value_type = float
    entity = TaxUnit
    label = "Gross foreign earned income and housing exclusions"
    unit = USD
    documentation = (
        "Gross exclusions under 26 U.S.C. 911(a): Form 2555 line 43, equal "
        "to the line 36 housing exclusion plus the line 42 foreign earned "
        "income exclusion, summed across both spouses on a joint return. "
        "This is before line 44 allocable deductions and excludes the line "
        "50 housing deduction and federal tax worksheet line 2b adjustments."
    )
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
    ]
    adds = [
        "foreign_earned_income_exclusion_amount",
        "foreign_housing_exclusion",
    ]
