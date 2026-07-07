from policyengine_us.model_api import *


class meets_snap_work_requirements_person(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = (
        "https://www.fns.usda.gov/snap/work-requirements",
        "https://www.law.cornell.edu/cfr/text/7/273.7#f_1",
        "https://www.law.cornell.edu/cfr/text/7/273.24#b",
        "https://www.law.cornell.edu/cfr/text/7/273.24#c_4",
    )

    def formula(person, period, parameters):
        general_work_requirements = person(
            "meets_snap_general_work_requirements", period
        )
        abawd_work_requirements = person("meets_snap_abawd_work_requirements", period)
        # This is the single source of truth for the household-child ABAWD
        # exception. 7 CFR 273.24(c)(4) exempts a person "residing in a
        # household where a household member is under age 18, even if the
        # household member who is under 18 is not himself eligible for SNAP
        # benefits." The exemption therefore keys on the presence of any
        # household member under the age threshold, not on tax-unit
        # dependency: a non-dependent under-18 household member (e.g., a teen
        # parent) triggers it. Post-HR1, 7 U.S.C. 2015(o)(3)(C) lowers the
        # threshold to 14 ("a parent or other member of a household with
        # responsibility for a dependent child under 14"), implemented
        # household-wide.
        # The threshold differs: pre-HR1 (18) vs post-HR1 (14).
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(period).gov.usda.snap.work_requirements.abawd.age_threshold
        # Snapshot pre-HR1 values (last month before 2025-07-04 effective date).
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(hr1_in_effect, p.dependent, p_pre.dependent)
        age = person("monthly_age", period)
        is_household_child = age < dep_threshold
        no_household_child = person.spm_unit.sum(is_household_child) == 0
        return where(
            no_household_child,
            abawd_work_requirements & general_work_requirements,
            general_work_requirements,
        )
