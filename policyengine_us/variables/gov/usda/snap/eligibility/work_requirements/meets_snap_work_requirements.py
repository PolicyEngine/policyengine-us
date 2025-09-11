from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        person = spm_unit.members
        meets_work_requirements_person = person(
            "meets_snap_work_requirements_person", period
        )

        return spm_unit.any(meets_work_requirements_person)
