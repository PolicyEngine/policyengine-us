from policyengine_us.model_api import *


class ok_ccs_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma Child Care Subsidy activity eligible"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-7",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.eligibility
        person = spm_unit.members
        is_parent_or_caretaker = person(
            "is_tax_unit_head_or_spouse", period.this_year
        ) | person("is_parent", period.this_year)
        weekly_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        monthly_hours = weekly_hours * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        monthly_earned_income = person("ok_ccs_countable_earned_income", period)
        effective_hourly_earnings = np.divide(
            monthly_earned_income,
            monthly_hours,
            out=np.zeros_like(monthly_earned_income),
            where=monthly_hours > 0,
        )
        min_wage = parameters(period).gov.dol.minimum_wage
        is_working = (weekly_hours >= p.minimum_weekly_work_hours) & (
            effective_hourly_earnings >= min_wage
        )
        is_student = person("is_full_time_student", period.this_year)
        is_in_k12_school = person("is_in_k12_school", period.this_year)

        parent_or_caretaker_count = spm_unit.sum(is_parent_or_caretaker)
        all_in_activity = (
            spm_unit.sum(is_parent_or_caretaker & ~(is_working | is_student)) == 0
        )
        has_working_parent_or_caretaker = (
            spm_unit.sum(is_parent_or_caretaker & is_working) > 0
        )
        has_k12_parent_or_caretaker = (
            spm_unit.sum(is_parent_or_caretaker & is_in_k12_school) > 0
        )
        # OAC 340:40-7-8(c)(1) approves care for one or both caretakers to
        # attend high school, while (c)(2) (high school equivalency) and
        # (c)(4) (postsecondary) require the other parent or caretaker in a
        # two-caretaker family to work during the same hours, so a
        # two-college-student couple does not qualify.
        education_pair_allowed = (
            (parent_or_caretaker_count == 1)
            | has_working_parent_or_caretaker
            | has_k12_parent_or_caretaker
        )
        modeled_eligible = (
            (parent_or_caretaker_count > 0) & all_in_activity & education_pair_allowed
        )
        # Protective or preventive child care covers families experiencing
        # homelessness, medical hardship, or natural disasters; the 30-day
        # initial approval limit is not tracked at the moment.
        protective = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        # Fall back to the CCDF activity-test input for approved activities not
        # individually modeled (SNAP E&T assigned activities and the
        # enrichment pathway for children receiving SSI, approved TANF Work
        # activities, and activity schedule overlap; OAC 340:40-7-7 and -7-8).
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return modeled_eligible | protective | meets_ccdf
