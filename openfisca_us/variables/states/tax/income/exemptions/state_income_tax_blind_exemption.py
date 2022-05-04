from openfisca_us.model_api import *


class state_income_tax_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax blind exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        amount = parameters(period).states.tax.income.exemptions.blind
        state = tax_unit.household("state_code_str", period)
        head_eligible = tax_unit("blind_head", period)
        spouse_eligible = tax_unit("blind_spouse", period)
        return amount[state] * (
            head_eligible.astype(int) + spouse_eligible.astype(int)
        )
