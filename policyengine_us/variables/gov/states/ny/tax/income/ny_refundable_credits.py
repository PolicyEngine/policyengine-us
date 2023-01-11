from policyengine_us.model_api import *


class ny_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    adds = "gov.states.ny.tax.income.credits.refundable"
