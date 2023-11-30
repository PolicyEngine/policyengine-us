from policyengine_us.model_api import *


class sc_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    adds = "gov.states.sc.tax.income.credits.non_refundable"
