from policyengine_us.model_api import *


class mt_non_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Montana refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.credits.non_refundable"
