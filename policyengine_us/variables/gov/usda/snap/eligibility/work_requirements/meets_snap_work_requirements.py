from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        general_work_requirements = person("meets_snap_general_work_requirements", period)
        abawd_work_requirements = person("meets_snap_abawd_work_requirements", period)
        work_ineligible_person = ~(general_work_requirements | abawd_work_requirements)
        return spm_unit.sum(work_ineligible_person) == 0
