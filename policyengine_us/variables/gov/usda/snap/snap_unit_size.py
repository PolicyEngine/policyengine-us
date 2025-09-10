from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit size"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        person = spm_unit.members
        ineligible_student = person("is_snap_ineligible_student", period)
        ineligible_students = spm_unit.sum(ineligible_student)
        
        eligible_adult = person("meets_snap_work_requirements_person", period)
        ineligible_adult = ~eligible_adult & ~ineligible_student
        ineligible_adults = spm_unit.sum(ineligible_adult)
        return max_(unit_size - ineligible_students - ineligible_adults, 0)
