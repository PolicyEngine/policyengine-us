from policyengine_us.model_api import *


class ar_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    adds = "gov.states.ar.tax.income.credits.non_refundable"
