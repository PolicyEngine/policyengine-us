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
        p_pre = parameters("2025-06-01").gov.usda.snap.work_requirements.abawd
        # (A) Age — 7 U.S.C. 2015(o)(3)(A)
        age = person("monthly_age", period)
        working_age_exempt = where(
            hr1_in_effect,
            p.age_threshold.exempted.calc(age),
            p_pre.age_threshold.exempted.calc(age),
        )
        # Work activity
        weekly_hours_worked = person(
            "weekly_hours_worked_before_lsr", period.this_year
        )
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
        work_reg_exempt = person(
            "is_snap_work_registration_exempt_non_age", period
        )
        # (E) Pregnant — 7 U.S.C. 2015(o)(3)(E)
        is_pregnant = person("is_pregnant", period)
        # State exemption
        state_code = person.household("state_code", period)
        state_code_str = state_code.decode_to_str()
        is_exempt_state = np.isin(state_code_str, p.exempt_states)
        base_conditions = (
            is_working
            | working_age_exempt
            | is_disabled
            | exempt_parent
            | work_reg_exempt
            | is_pregnant
            | is_exempt_state
        )
        # Pre-HR1 exemptions: homeless, veteran
        is_homeless = person.household("is_homeless", period)
        is_veteran = person("is_veteran", period)
        return where(
            hr1_in_effect,
            base_conditions,
            base_conditions | is_homeless | is_veteran,
        )
