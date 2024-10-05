from policyengine_us.model_api import *


class de_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = "gov.states.de.tax.income.credits.non_refundable"
