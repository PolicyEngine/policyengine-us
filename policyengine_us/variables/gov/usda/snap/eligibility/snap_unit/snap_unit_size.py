from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit size"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        person = spm_unit.members
        eligible_person = person("is_snap_demographic_eligible_person", period)
        ineligible_people = spm_unit.sum(~eligible_person)

        return max_(unit_size - ineligible_people, 0)
