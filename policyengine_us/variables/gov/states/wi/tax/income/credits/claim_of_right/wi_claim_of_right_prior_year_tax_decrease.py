from policyengine_us.model_api import *


class wi_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "Wisconsin prior-year tax decrease from excluding repaid claim of right income"
    )
    unit = USD
    documentation = (
        "Decrease in Wisconsin income tax for the earlier year that would "
        "be attributable to subtracting the income repaid this year "
        "(claim_of_right_repayment): the tax shown on the return for the "
        "earlier year less that tax refigured without the repaid income "
        "(Form 1 instructions, line 32). The tax unit uses the sum for its "
        "head and spouse."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/1",
        # 2025 Form 1 instructions, line 32
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )
    defined_for = StateCode.WI
