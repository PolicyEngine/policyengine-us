from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit size"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        person = spm_unit.members
        ineligible = person("is_snap_ineligible_student", period) | ~person(
            "is_snap_immigration_status_eligible", period
        )
        ineligible_count = spm_unit.sum(ineligible)
        return max_(unit_size - ineligible_count, 0)
