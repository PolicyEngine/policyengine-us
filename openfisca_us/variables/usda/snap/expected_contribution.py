from openfisca_us.model_api import *


class snap_expected_contribution_towards_food(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Expected food contribution from SNAP net income"
    label = "SNAP expected food contribution"
    unit = "currency-USD"

    def formula(spm_unit, period, parameters):
        expected_food_contribution = parameters(
            period
        ).usda.snap.expected_food_contribution
        return spm_unit("snap_net_income", period) * expected_food_contribution
