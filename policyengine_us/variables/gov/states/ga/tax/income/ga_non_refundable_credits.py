from policyengine_us.model_api import *


class ga_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    adds = "gov.states.ga.tax.income.credits.non_refundable"
