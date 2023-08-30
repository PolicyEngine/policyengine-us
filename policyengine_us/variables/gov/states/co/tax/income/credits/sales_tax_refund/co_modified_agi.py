from policyengine_us.model_api import *


class co_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado modified adjusted gross income for TABOR"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        fed_agi = tax_unit("adjusted_gross_income", period)
        social_security = tax_unit("tax_exempt_social_security", period)
        interest_income = tax_unit("tax_exempt_interest_income", period)
        