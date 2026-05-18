from policyengine_us.model_api import *


class tn_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TN
    adds = "gov.states.tn.tax.income.credits.refundable"
