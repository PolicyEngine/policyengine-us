from policyengine_us.model_api import *


class wa_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "WA refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    adds = ["wa_working_families_tax_credit"]
