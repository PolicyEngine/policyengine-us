from policyengine_us.model_api import *


class wv_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = "gov.states.wv.tax.income.credits.non_refundable"
