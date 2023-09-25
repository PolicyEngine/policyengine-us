from policyengine_us.model_api import *


class ky_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    adds = "gov.states.ky.tax.income.credits.non_refundable"
