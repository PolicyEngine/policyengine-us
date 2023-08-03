from policyengine_us.model_api import *


class ut_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "exempt from Utah income tax"
    unit = USD
    documentation = "Form TC-40, line 21"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        basic_standard_deduction = tax_unit("basic_standard_deduction", period)
        return federal_agi <= basic_standard_deduction
