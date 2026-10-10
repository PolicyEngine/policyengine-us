from policyengine_us.model_api import *


class ga_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = "Georgia prior-year tax decrease from excluding repaid claim of right income"
    unit = USD
    documentation = (
        "Decrease in Georgia income tax for the earlier year or years, "
        "computed as if the person had not received the income repaid this "
        "year (claim_of_right_repayment). The tax unit uses the sum for its "
        "head and spouse."
    )
    definition_period = YEAR
    reference = (
        # 2025 IT-511, Form 500 line 25, Claim of right under IRC 1341
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=18",
    )
    defined_for = StateCode.GA
