from policyengine_us.model_api import *


class wa_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA

    adds = "gov.states.wa.tax.income.credits.refundable"
