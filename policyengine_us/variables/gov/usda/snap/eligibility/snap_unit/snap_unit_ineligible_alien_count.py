from policyengine_us.model_api import *


class snap_unit_ineligible_alien_count(Variable):
    value_type = int
    entity = SPMUnit
    label = (
        "Number of ineligible people in SNAP unit due to immigration status"
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        immigration_status_eligible = spm_unit.members(
            "snap_immigration_status_eligible", period
        )

        return spm_unit.sum(~immigration_status_eligible)
