from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        general_work_requirements = person(
            "meets_snap_general_work_requirements", period
        )
        abawd_work_requirements = person(
            "meets_snap_abawd_work_requirements", period
        )
        # Dependent child threshold differs: pre-HR1 (18) vs post-HR1 (14)
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(hr1_in_effect, p.dependent, p_pre.dependent)
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < dep_threshold
        no_dependent_child = person.spm_unit.sum(is_dependent & is_child) == 0
        meets_work_requirements_person = where(
            no_dependent_child,
            abawd_work_requirements & general_work_requirements,
            general_work_requirements,
        )
        return spm_unit.sum(~meets_work_requirements_person) == 0
