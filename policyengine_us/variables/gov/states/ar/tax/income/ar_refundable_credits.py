from policyengine_us.model_api import *


class ar_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    adds = "gov.states.ar.tax.income.credits.refundable"
