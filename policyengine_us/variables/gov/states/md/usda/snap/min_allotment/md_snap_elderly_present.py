from policyengine_us.model_api import *


class md_snap_elderly_present(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Elderly person is present for the Maryland SNAP minimum allotment"
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        elderly = person("md_snap_is_elderly", period)
        return spm_unit.any(elderly)
