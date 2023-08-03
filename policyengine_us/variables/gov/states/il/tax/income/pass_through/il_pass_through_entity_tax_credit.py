from policyengine_us.model_api import *


class il_pass_through_entity_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Pass-Through Entity Tax Credit"
    unit = USD
    definition_period = YEAR
