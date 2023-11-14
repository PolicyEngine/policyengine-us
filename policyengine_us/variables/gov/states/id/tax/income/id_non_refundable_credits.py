from policyengine_us.model_api import *


class id_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    adds = "gov.states.id.tax.income.credits.non_refundable"
