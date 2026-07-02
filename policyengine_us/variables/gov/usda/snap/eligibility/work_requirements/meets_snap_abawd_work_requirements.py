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
        # Work activity — 7 U.S.C. 2015(o)(2); 7 CFR 273.24(a)(1):
        # (i) work 20+ hours per week, (ii) participate in and comply
        # with a qualifying work program 20+ hours per week, or
        # (iii) any combination of work and work program participation
        # totaling 20+ hours per week.
        weekly_hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        work_program_hours = person("weekly_snap_work_program_hours", period.this_year)
        combined_weekly_hours = weekly_hours_worked + work_program_hours
        meets_hours_threshold = combined_weekly_hours >= p.weekly_hours_threshold
        # (iv) participate in and comply with a workfare program under
        # 7 CFR 273.7(m), which satisfies the requirement regardless of
        # hours.
        is_workfare_participant = person("is_snap_workfare_participant", period)
        is_working = meets_hours_threshold | is_workfare_participant
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
        # Pre-HR1 exemptions: homeless, veteran
        is_homeless = person.household("is_homeless", period)
        is_veteran = person("is_veteran", period)
        post_hr1_conditions = base_conditions | is_indian_exempt
        pre_hr1_conditions = base_conditions | is_homeless | is_veteran
        return where(
            hr1_in_effect,
            post_hr1_conditions,
            pre_hr1_conditions,
        )
