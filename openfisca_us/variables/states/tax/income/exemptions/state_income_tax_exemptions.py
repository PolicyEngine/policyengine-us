from openfisca_us.model_api import *


class state_income_tax_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax exemptions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        exemptions = parameters(period).states.tax.income.exemptions
        state = tax_unit.household("state_code_str", period)
        filing_status = tax_unit("filing_status", period)
        dependents = tax_unit("tax_unit_dependents", period)
        personal_exemption = exemptions.personal[state][filing_status]
        dependent_exemption = exemptions.dependent[state] * dependents
        return personal_exemption + dependent_exemption
