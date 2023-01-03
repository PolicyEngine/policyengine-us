from policyengine_us.model_api import *


class or_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        income_after_subtractions = tax_unit(
            "or_income_after_subtractions", period
        )
        deductions = tax_unit("or_deductions", period)
        return max_(income_after_subtractions - deductions, 0)
