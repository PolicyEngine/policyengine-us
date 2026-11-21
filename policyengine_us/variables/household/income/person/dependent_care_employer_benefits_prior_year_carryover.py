from policyengine_us.model_api import *


class dependent_care_employer_benefits_prior_year_carryover(Variable):
    value_type = float
    entity = Person
    label = "Prior-year dependent care benefits used in this year's grace period"
    documentation = (
        "Unused employer dependent care benefits from the prior year's plan "
        "that the employee used during this year's grace period (Form 2441 "
        "line 13, FTB 3506 line 14). The prior year's W-2 box 10 reported "
        "them, so this year's dependent_care_employer_benefits leaves them "
        "out. They count toward this year's IRC 129 exclusion and taxable "
        "benefits. For 2021 and 2022, when Form 2441 line 21 adds line 13 to "
        "the cap under temporary relief rules, the federal calculation leaves "
        "this amount out of both (prior_year_carryover_omitted). California "
        "counts it in every year, and Alabama's 2021 recompute under 2020 "
        "rules counts it."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
        # FTB 3506 line 14: "Enter the amount from federal Form 2441, line 13."
        "https://www.ftb.ca.gov/forms/2021/2021-3506-instructions.html",
    )
