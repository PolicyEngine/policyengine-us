from policyengine_us.model_api import *


class mi_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.credits.refundable"
