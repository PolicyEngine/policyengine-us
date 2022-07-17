from openfisca_us.model_api import *


class il_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        ADDITIONS = ["adjusted_gross_income", "tax_exempt_interest_income", "dividend_income", "il_schedule_m_additions"]
        SUBTRACTIONS = ["social_security_benefits", "schedule_m_subtractions"]
        return add(tax_unit, period, ADDITIONS) - add(tax_unit, period, SUBTRACTIONS)