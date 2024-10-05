from policyengine_us.model_api import *


class de_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = "gov.states.de.tax.income.credits.refundable"
