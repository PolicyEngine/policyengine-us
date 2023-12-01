from policyengine_us.model_api import *


class id_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    adds = "gov.states.id.tax.income.credits.refundable"
