from policyengine_us.model_api import *


class meets_snap_abawd_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81",
    )

    def formula(person, period, parameters):
        hr1_in_effect = person("is_snap_abawd_hr1_in_effect", period)
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        # Snapshot pre-HR1 values (last month before 2025-07-04 effective date).
        p_pre = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        # (A) Age — 7 U.S.C. 2015(o)(3)(A)
        age = person("monthly_age", period)
        working_age_exempt = where(
            hr1_in_effect,
            p.age_threshold.exempted.calc(age),
            p_pre.age_threshold.exempted.calc(age),
        )
        # Work activity
        weekly_hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_working = weekly_hours_worked >= p.weekly_hours_threshold
        # (B) Disability — 7 U.S.C. 2015(o)(3)(B)
        is_disabled = person("is_disabled", period)
        # (C) Parent with qualifying child — 7 U.S.C. 2015(o)(3)(C)
        is_dependent = person("is_tax_unit_dependent", period)
        dep_threshold = where(
            hr1_in_effect,
            p.age_threshold.dependent,
            p_pre.age_threshold.dependent,
        )
        is_qualifying_child = age < dep_threshold
        is_parent = person("is_parent", period)
        has_child = person.spm_unit.any(is_dependent & is_qualifying_child)
        exempt_parent = is_parent & has_child
        # (D) Work registration exempt (non-age) — 7 U.S.C. 2015(o)(3)(D)
        work_reg_exempt = person("is_snap_work_registration_exempt_non_age", period)
        # (E) Pregnant — 7 U.S.C. 2015(o)(3)(E)
        is_pregnant = person("is_pregnant", period)
        # (F)-(G) Indian, Urban Indian, or California Indian.
        is_indian_exempt = person("is_snap_abawd_indian_exempt", period)
        # TODO: HI/AK delayed adoption (2025-11-01) to be handled
        # in a follow-up PR via state-level hr1_in_effect parameters.
        base_conditions = (
            is_working
            | working_age_exempt
            | is_disabled
            | exempt_parent
            | work_reg_exempt
            | is_pregnant
        )
        # Pre-HR1 exemptions: homeless, veteran, former foster youth
        is_homeless = person.household("is_homeless", period)
        is_veteran = person("is_veteran", period)
        # 7 CFR 273.24(c)(9): aged 24 or younger and in foster care under
        # State responsibility on their 18th birthday (added by the Fiscal
        # Responsibility Act of 2023, removed by P.L. 119-21).
        was_in_foster_care = person("was_in_foster_care", period)
        former_foster_youth = was_in_foster_care & (
            age <= p_pre.age_threshold.former_foster_care
        )
        post_hr1_conditions = base_conditions | is_indian_exempt
        pre_hr1_conditions = (
            base_conditions | is_homeless | is_veteran | former_foster_youth
        )
        return where(
            hr1_in_effect,
            post_hr1_conditions,
            pre_hr1_conditions,
        )
