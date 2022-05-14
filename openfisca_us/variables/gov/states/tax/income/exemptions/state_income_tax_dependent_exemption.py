from openfisca_us.model_api import *


class state_income_tax_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax dependent exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        exemptions = parameters(period).states.tax.income.exemptions
        state = tax_unit.household("state_code_str", period)
        dependents = tax_unit("tax_unit_dependents", period)
        return exemptions.dependent[state] * dependents
