from policyengine_us.model_api import *


class la_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana refundable credits"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    adds = "gov.states.la.tax.income.credits.refundable"
