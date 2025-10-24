from policyengine_us.model_api import *


class pr_income_tax(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Puerto Rico income tax"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=3"
    defined_for = StateCode.PR

    adds = ["pr_regular_tax_before_credits"]
    subtracts = ["pr_refundable_credits"]
