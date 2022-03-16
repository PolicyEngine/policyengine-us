from openfisca_us.model_api import *


class posagi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Positive AGI"
    unit = USD
    documentation = "Negative AGI values capped at zero"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(tax_unit("c00100", period), 0)


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI"
    documentation = "Adjusted Gross Income"
    unit = USD

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["ymod1", "c02500", "c02900"])


adjusted_gross_income = variable_alias("adjusted_gross_income", c00100)
