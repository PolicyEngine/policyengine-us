from policyengine_us.model_api import *


class mo_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO
    adds = "gov.states.mo.tax.income.credits.refundable"
