from policyengine_us.model_api import *


class vt_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    adds = "gov.states.vt.tax.income.credits.refundable"
