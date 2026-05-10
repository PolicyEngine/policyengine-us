from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = (
        "https://www.fns.usda.gov/snap/work-requirements",
        # 7 CFR 273.7(f)(1) — general work requirement; individual
        # disqualification is the default rule.
        "https://www.law.cornell.edu/cfr/text/7/273.7#f_1",
        # 7 CFR 273.24(b) — ABAWD time limit; always individual.
        "https://www.law.cornell.edu/cfr/text/7/273.24#b",
    )

    def formula(spm_unit, period, parameters):
        # Per 7 CFR 273.7(f)(1) and 273.24(b), a non-compliant member is
        # individually disqualified and excluded from the SNAP unit.
        # Remaining members continue to receive SNAP. The unit remains
        # eligible on the work-requirement dimension so long as at least
        # one member meets requirements or is exempt.
        #
        # The narrow 7 CFR 273.7(f)(5) state option — elected by 8
        # jurisdictions (AZ, FL, MA, MN, MS, TX, VA, VI) — permitting
        # household-wide disqualification when the head of household
        # fails the general work requirement, bounded to at most 180
        # days, is not yet parameterized here.
        person = spm_unit.members
        # ABAWD time-limit failures apply only when the household has no
        # dependent child under the applicable age threshold.
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(period).gov.usda.snap.work_requirements.abawd.age_threshold
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(hr1_in_effect, p.dependent, p_pre.dependent)
        age = person("monthly_age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < dep_threshold
        no_dependent_child = person.spm_unit.sum(is_dependent & is_child) == 0
        abawd_disqualified = no_dependent_child & ~person(
            "meets_snap_abawd_work_requirements", period
        )
        disqualified = (
            person("is_snap_work_requirements_disqualified", period)
            | abawd_disqualified
        )
        return spm_unit.any(~disqualified)
