from policyengine_us.model_api import *


class dependent_care_assistance_qualified_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified expenses for employer dependent care assistance"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/129#e_1",
        "https://www.law.cornell.edu/uscode/text/26/21#b_2",
        # PDF pages 1 and 5: qualified expenses and Form 2441 line 16.
        "https://www.irs.gov/pub/irs-prior/i2441--2017.pdf#page=1",
        # PDF pages 2 and 5: qualified expenses and Form 2441 line 16.
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=2",
    )
    # Independently supplied employment-related expenses for qualifying care
    # incurred this year, regardless of when paid, before employer benefits
    # and statutory dollar/earnings limits, after disallowed reimbursements.
    # Include eligible employer-paid care and disabled-adult/spousal care.
    # Apply the year's reimbursement rules: the 2017 instructions retain
    # state reimbursements included in income. Do not infer a change from
    # the shorter wording in later instructions.
    # Unreported expenses are modeled as zero, not established as zero.
    # Neither W-2 box 10 nor gross bills establish this qualified amount;
    # deriving it from modeled subsidies would create an AGI dependency cycle.
    # See docs/gov/irs/historical-validation.md for the caller assumptions.
