from policyengine_us.model_api import *


class pr_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"

    adds = ["pr_agi_person"]
