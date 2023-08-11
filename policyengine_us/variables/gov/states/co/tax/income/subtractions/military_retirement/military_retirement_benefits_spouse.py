from policyengine_us.model_api import *


class military_retirement_benefits_spouse(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado military retirement benefits for spouse"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR
