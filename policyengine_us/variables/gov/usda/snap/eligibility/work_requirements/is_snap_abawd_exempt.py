from policyengine_us.model_api import *


class is_snap_abawd_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Person is exempt from the SNAP ABAWD time limit"
    definition_period = MONTH
    documentation = (
        "Whether the person is exempt from the Able-Bodied Adult Without "
        "Dependents (ABAWD) time limit under 7 U.S.C. 2015(o)(3) and 7 CFR "
        "273.24, independent of whether they are currently meeting the work "
        "requirement. This is the exemption ('subject-to') test only: a person "
        "who is NOT exempt is subject to the ABAWD requirement even if they "
        "comply with it. meets_snap_abawd_work_requirements adds the "
        "work-activity compliance test on top of this exemption set; the "
        "Medicaid community engagement pass-through uses the negation of this "
        "variable to capture people subject only to the ABAWD requirement "
        "(e.g. post-HR1 adults aged 60-64, who are exempt from the general "
        "SNAP work requirement but subject to the ABAWD time limit)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.law.cornell.edu/uscode/text/7/2015#o",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=11",
    )

    def formula(person, period, parameters):
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        # Snapshot pre-HR1 values (last month before 2025-07-04 effective date).
        p_pre = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        # (A) Age — 7 U.S.C. 2015(o)(3)(A). Ages outside the ABAWD range are
        # exempt; HR1 (P.L. 119-21) raised the upper bound from 54 to 64.
        age = person("monthly_age", period)
        working_age_exempt = where(
            hr1_in_effect,
            p.age_threshold.exempted.calc(age),
            p_pre.age_threshold.exempted.calc(age),
        )
        # (B) Disability — 7 U.S.C. 2015(o)(3)(B)
        is_disabled = person("is_disabled", period)
        # (D) Work registration exempt (non-age) — 7 U.S.C. 2015(o)(3)(D),
        # including the 7 CFR 273.7(b)(1)(vii) exemption for people working
        # 30 or more hours weekly.
        work_reg_exempt = person("is_snap_work_registration_exempt_non_age", period)
        # (E) Pregnant — 7 U.S.C. 2015(o)(3)(E)
        is_pregnant = person("is_pregnant", period)
        # (F)-(G) Indian, Urban Indian, or California Indian.
        is_indian_exempt = person("is_snap_abawd_indian_exempt", period)
        # State discretionary exemption — 7 U.S.C. 2015(o)(6).
        is_discretionary_exempt = person("is_snap_abawd_discretionary_exempt", period)
        # Area waiver — 7 U.S.C. 2015(o)(4), 7 CFR 273.24(f).
        in_waived_area = person("is_in_snap_abawd_waived_area", period)
        exempt_base = (
            working_age_exempt
            | is_disabled
            | work_reg_exempt
            | is_pregnant
            | is_discretionary_exempt
            | in_waived_area
        )
        # Pre-HR1 exemptions: homeless, veteran, former foster youth.
        is_homeless = person.household("is_homeless", period)
        is_veteran = person("is_veteran", period)
        # 7 CFR 273.24(c)(9): aged 24 or younger and in foster care under
        # State responsibility on their 18th birthday (added by the Fiscal
        # Responsibility Act of 2023, removed by P.L. 119-21).
        was_in_foster_care = person("was_in_foster_care", period)
        former_foster_youth = was_in_foster_care & (
            age <= p_pre.age_threshold.former_foster_care
        )
        post_hr1_exempt = exempt_base | is_indian_exempt
        pre_hr1_exempt = exempt_base | is_homeless | is_veteran | former_foster_youth
        # Good-faith-effort exemption window — 7 U.S.C. 2015(o)(7). A
        # noncontiguous State that has adopted HR1 may temporarily retain a
        # specified set of pre-HR1 exceptions on top of the post-HR1 set.
        in_good_faith_window = person(
            "is_snap_abawd_in_good_faith_exemption_window", period
        )
        retained_age_exempt = age >= p.good_faith_exemption.retained_age_minimum
        window_exempt = (
            post_hr1_exempt
            | retained_age_exempt
            | is_homeless
            | is_veteran
            | former_foster_youth
        )
        return where(
            hr1_in_effect,
            where(in_good_faith_window, window_exempt, post_hr1_exempt),
            pre_hr1_exempt,
        )
