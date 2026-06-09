from policyengine_us.model_api import *


class pa_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    adds = ["pa_income_tax_after_forgiveness"]
