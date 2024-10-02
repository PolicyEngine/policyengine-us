from policyengine_us.model_api import *


class pa_refundable_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    adds = "gov.states.pa.tax.income.credits.refundable"
