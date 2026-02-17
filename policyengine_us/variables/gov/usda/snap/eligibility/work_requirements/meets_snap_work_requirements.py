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
        # CA delays HR1 ABAWD changes to June 1, 2026 (ACL 25-93)
        state_code = person.household("state_code", period)
        is_ca = state_code == StateCode.CA
        ca_hr1 = parameters(
            period
        ).gov.states.ca.cdss.snap.work_requirements.abawd.hr1_in_effect
        use_ca_pre_hr1 = is_ca & ~ca_hr1
        federal_abawd = person("meets_snap_abawd_work_requirements", period)
        ca_abawd = person("ca_meets_snap_abawd_work_requirements", period)
        abawd_work_requirements = where(
            use_ca_pre_hr1, ca_abawd, federal_abawd
        )
        # Dependent child threshold differs: pre-HR1 (18) vs post-HR1 (14)
        p = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(use_ca_pre_hr1, p_pre.dependent, p.dependent)
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
