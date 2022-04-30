from openfisca_us.model_api import *


class is_state_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Exempt from state income tax"
    unit = USD
    documentation = "Exempt from state income tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).states.tax.income.exempt
        state = tax_unit.household("state_code_str", period)
        mars = tax_unit("marital_status", period)
        dependents = tax_unit("tax_unit_dependents", period)
        agi = tax_unit("adjusted_gross_income", period)
        base_limit = p.limit[state][mars]
        dep_limit = dependents * p.dependent[state][mars]
        limit = base_limit + dep_limit
        return agi <= limit
