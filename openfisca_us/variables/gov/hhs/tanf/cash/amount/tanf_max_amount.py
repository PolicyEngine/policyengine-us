from openfisca_us.model_api import *


class tanf_max_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF maximum benefit"
    documentation = "The maximum benefit amount a family could receive from Temporary Assistance for Needy Families given their state and family size."
    unit = USD

    def formula(spm_unit, period, parameters):
        household_size = spm_unit("spm_unit_size", period).astype(str)
        state = spm_unit.household("state_code_str", period)
        max_amount = parameters(period).hhs.tanf.cash.amount.max
        return max_amount[state][household_size] * MONTHS_IN_YEAR
