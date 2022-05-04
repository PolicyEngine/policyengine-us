from openfisca_us.model_api import *


class state_income_tax_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax personal exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        exemptions = parameters(period).states.tax.income.exemptions
        state = tax_unit.household("state_code_str", period)
        filing_status = tax_unit("filing_status", period)
        return exemptions.personal[state][filing_status]
