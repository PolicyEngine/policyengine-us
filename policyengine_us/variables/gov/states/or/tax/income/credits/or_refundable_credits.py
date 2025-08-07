from policyengine_us.model_api import *


class or_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    adds = "gov.states.or.tax.income.credits.refundable"
