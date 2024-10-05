from policyengine_us.model_api import *


class il_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL nonrefundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = "gov.states.il.tax.income.credits.nonrefundable"
