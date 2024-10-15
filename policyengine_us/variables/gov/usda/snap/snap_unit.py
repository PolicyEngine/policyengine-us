from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        person = spm_unit.members
        ineligible_student = person("is_snap_ineligible_student", period)
        ineligible_students = spm_unit.sum(ineligible_student)
        return max_(unit_size - ineligible_students, 0)
