from policyengine_us.model_api import *


class tax_exempt_railroad_pension_benefits(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt Railroad Retirement pension benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The part of Form RRB-1099-R benefits that recovers the employee's "
        "own contributions tax free. IRC 72(r)(2) treats tier 2 employee "
        "taxes as employee contributions to the plan, and the annuitant "
        "recovers them over the annuity's expected life, usually under the "
        "Simplified Method."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#r_2",
        # IRS Pub. 575 (2024): tax-free recovery of employee contributions
        # from tier 2 and the non-social security equivalent part of tier 1.
        "https://www.irs.gov/pub/irs-prior/p575--2024.pdf#page=7",
    )
