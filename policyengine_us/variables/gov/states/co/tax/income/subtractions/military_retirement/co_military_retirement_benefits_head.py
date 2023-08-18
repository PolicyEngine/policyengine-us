from policyengine_us.model_api import *


class co_military_retirement_benefits_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado military retirement benefits for head"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR
