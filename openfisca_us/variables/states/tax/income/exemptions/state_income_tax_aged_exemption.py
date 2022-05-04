from itertools import count
from openfisca_us.model_api import *


class state_income_tax_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax aged exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).states.tax.income.exemptions.aged
        state = tax_unit.household("state_code_str", period)
        age_limit = p.age[state]
        head_eligible = tax_unit("age_head", period) >= age_limit
        spouse_eligible = tax_unit("age_spouse", period) >= age_limit
        return p.amount[state] * (
            head_eligible.astype(int) + spouse_eligible.astype(int)
        )
