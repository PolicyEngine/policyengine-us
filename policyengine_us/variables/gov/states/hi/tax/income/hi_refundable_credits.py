from policyengine_us.model_api import *


class hi_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = "gov.states.hi.tax.income.credits.refundable"
