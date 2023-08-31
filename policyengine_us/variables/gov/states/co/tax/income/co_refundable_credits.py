from policyengine_us.model_api import *


class co_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = "gov.states.co.tax.income.credits.refundable"
