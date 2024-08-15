from policyengine_us.model_api import *


class positive_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Positive Gross Income"
    unit = USD
    documentation = "Negative gross income values capped at zero"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["irs_gross_income"])
        return max_(gross_income, 0)
