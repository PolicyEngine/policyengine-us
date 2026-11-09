from policyengine_us.model_api import *


class hi_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = TaxUnit
    label = "Prior-year Hawaii tax decrease from excluding repaid claim of right income"
    unit = USD
    documentation = (
        "Decrease in Hawaii income tax for the earlier year or years from "
        "excluding the income repaid this year: the tax on each earlier "
        "Hawaii return less that tax refigured without the repaid income "
        "(Form N-364, lines 4 to 6, summed over the earlier years)."
    )
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf"
    defined_for = StateCode.HI
