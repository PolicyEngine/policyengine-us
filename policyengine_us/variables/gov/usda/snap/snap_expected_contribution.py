from policyengine_us.model_api import *


class snap_expected_contribution(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Expected food contribution from SNAP net income"
    label = "SNAP expected food contribution"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"

    def formula(spm_unit, period, parameters):
        expected_food_contribution = parameters(
            period
        ).gov.usda.snap.expected_contribution
        return (
            np.floor(spm_unit("snap_net_income", period))
            * expected_food_contribution
        )
