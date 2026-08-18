from policyengine_us.model_api import *


class is_subject_to_snap_abawd(Variable):
    value_type = bool
    entity = Person
    label = "Person is subject to the SNAP ABAWD time limit"
    definition_period = MONTH
    documentation = (
        "Whether the person is subject to the Able-Bodied Adult Without "
        "Dependents (ABAWD) time limit: an able-bodied adult without "
        "dependents (no household member under the dependent-age threshold, "
        "per 7 CFR 273.24(c)(4)) who is not otherwise exempt "
        "(is_snap_abawd_exempt). This is a status test independent of "
        "compliance: a person who works enough to satisfy the requirement is "
        "still subject to it. Used by the Medicaid community engagement "
        "pass-through, which excludes people subject to a SNAP work "
        "requirement (general or ABAWD)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.law.cornell.edu/uscode/text/7/2015#o",
    )

    def formula(person, period, parameters):
        is_exempt = person("is_snap_abawd_exempt", period)
        # "Without dependents" applicability — mirrors the household-child
        # gate in meets_snap_work_requirements_person (7 CFR 273.24(c)(4)):
        # a person residing with any household member under the dependent-age
        # threshold is not subject to the ABAWD time limit. HR1 lowers the
        # threshold to 14; a good-faith-effort window retains the pre-HR1
        # threshold (18).
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        in_good_faith_window = person(
            "is_snap_abawd_in_good_faith_exemption_window", period
        )
        p = parameters(period).gov.usda.snap.work_requirements.abawd.age_threshold
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(
            hr1_in_effect & ~in_good_faith_window, p.dependent, p_pre.dependent
        )
        age = person("monthly_age", period)
        is_household_child = age < dep_threshold
        no_household_child = person.spm_unit.sum(is_household_child) == 0
        return no_household_child & ~is_exempt
