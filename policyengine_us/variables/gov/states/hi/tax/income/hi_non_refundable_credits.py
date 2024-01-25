from policyengine_us.model_api import *


class hi_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = "gov.states.hi.tax.income.credits.non_refundable"
