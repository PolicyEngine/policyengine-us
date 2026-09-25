from policyengine_us.model_api import *


class has_snap_abawd_household_child(Variable):
    value_type = bool
    entity = Person
    label = "Person resides with a household member under the SNAP ABAWD dependent-age threshold"
    definition_period = MONTH
    documentation = (
        "Single source of truth for the ABAWD household-child gate: whether "
        "the person resides with a household member under the dependent-age "
        "threshold, which routes them around the Able-Bodied Adult Without "
        "Dependents (ABAWD) time limit. 7 CFR 273.24(c)(4) frames the gate "
        "household-wide: it covers a person 'residing in a household where a "
        "household member is under age 18, even if the household member who "
        "is under 18 is not himself eligible for SNAP benefits', keying on "
        "the presence of any household member under the age threshold rather "
        "than on tax-unit dependency. Post-HR1, 7 U.S.C. 2015(o)(3)(C) "
        "(P.L. 119-21) lowers the threshold to a dependent child under 14, "
        "implemented household-wide per the pre-existing regulatory "
        "construction. During an approved good-faith-effort exemption window "
        "(7 U.S.C. 2015(o)(7); currently Alaska, 2025-11-01 through "
        "2026-10-31), the State temporarily retains the pre-HR1 threshold "
        "(18), so a household with a child aged 14-17 keeps the exemption "
        "even though HR1 is otherwise in effect."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24#c_4",
        "https://www.law.cornell.edu/uscode/text/7/2015#o_3",
    )

    def formula(person, period, parameters):
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        in_good_faith_window = person(
            "is_snap_abawd_in_good_faith_exemption_window", period
        )
        p = parameters(period).gov.usda.snap.work_requirements.abawd.age_threshold
        # Snapshot pre-HR1 values (last month before 2025-07-04 effective date).
        p_pre = parameters(
            "2025-06-01"
        ).gov.usda.snap.work_requirements.abawd.age_threshold
        dep_threshold = where(
            hr1_in_effect & ~in_good_faith_window, p.dependent, p_pre.dependent
        )
        age = person("monthly_age", period)
        is_household_child = age < dep_threshold
        return person.spm_unit.any(is_household_child)
