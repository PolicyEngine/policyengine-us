from openfisca_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP benefit entitlement"
    reference = "United States Code, Title 7, Section 2017(a)"
    unit = "currency-USD"

    def formula(spm_unit, period):
        max_benefit = spm_unit("snap_max_benefit", period)
        expected_contribution = spm_unit(
            "snap_expected_contribution_towards_food", period
        )
        return max_benefit - expected_contribution
