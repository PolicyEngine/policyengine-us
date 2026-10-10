from policyengine_us.model_api import *


class ok_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "Oklahoma prior-year tax decrease from excluding repaid claim of right income"
    )
    unit = USD
    documentation = (
        "Decrease in Oklahoma income tax for the year or years the income "
        "repaid this year (claim_of_right_repayment) was received, from "
        "excluding that income from federal adjusted gross income on amended "
        "Oklahoma returns for those years. The tax unit uses the sum for its "
        "head and spouse."
    )
    definition_period = YEAR
    reference = (
        # OAC 710:50-3-9(b)
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/resources/rules-and-policies/agency-rules/2026/Chapter50-Income-2026.pdf#page=16",
    )
    defined_for = StateCode.OK
