from policyengine_us.model_api import *


class az_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = "gov.states.az.tax.income.credits.non_refundable"
