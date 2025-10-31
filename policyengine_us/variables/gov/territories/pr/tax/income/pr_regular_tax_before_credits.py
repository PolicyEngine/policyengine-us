from policyengine_us.model_api import *


class pr_regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico regular tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=19"
