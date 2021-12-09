from openfisca_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP benefit entitlement"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = "currency-USD"

    def formula(spm_unit, period):
        max_benefit = spm_unit("snap_max_benefit", period)
        expected_contribution = spm_unit(
            "snap_expected_contribution_towards_food", period
        )
        return max_(0, max_benefit - expected_contribution)
