from policyengine_us.model_api import *


class pr_gradual_adjustment_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico gradual adjustment amount"
    documentation = (
        "An additional amount added to tax amount for high income filers."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "pr_gradual_adjustment_eligibility"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=3"
