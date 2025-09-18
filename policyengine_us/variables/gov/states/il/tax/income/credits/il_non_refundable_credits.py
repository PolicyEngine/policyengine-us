from policyengine_us.model_api import *


class il_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = "gov.states.il.tax.income.credits.non_refundable"
