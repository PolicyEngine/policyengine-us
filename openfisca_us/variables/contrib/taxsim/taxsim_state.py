from openfisca_us.model_api import *


class taxsim_state(Variable):
    value_type = float
    entity = TaxUnit
    label = "State code"
    documentation = 'SOI codes. These run from 1 for Alabama to 51 for Wyoming and are not the Census or PSID codes. See state list,and also item two above.). Use zero for "no state tax calculation"'
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        state_code_str = tax_unit.household("state_code_str", period)
        return select(
            [
                state_code_str == "MD",
                state_code_str == "MA",
                state_code_str == "NY",
                state_code_str == "WA",
                True,
            ],
            [
                21,
                22,
                33,
                48,
                0,
            ],
        )
