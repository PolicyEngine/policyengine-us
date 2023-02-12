from policyengine_us.model_api import *


class il_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois refundable credits"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.IL

    adds = "gov.states.il.tax.income.credits.refundable"
