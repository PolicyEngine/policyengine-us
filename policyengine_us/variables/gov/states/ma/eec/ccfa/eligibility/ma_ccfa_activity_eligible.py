from policyengine_us.model_api import *


class ma_ccfa_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Activity eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=42",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=34",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.activity_requirements
        person = spm_unit.members
        parent = person("ma_ccfa_is_parent", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        student = person("is_full_time_student", period.this_year)
        disabled = person("is_disabled", period.this_year)
        # Retirement is a service need only for parents aged 65 or older.
        # is_retired defaults to age 65 or older, so this matches the age gate
        # unless a caller reports that the parent is not retired.
        retired = (person("age", period.this_year) >= p.work_exempt_age) & person(
            "is_retired", period.this_year
        )
        individually_eligible = (hours >= p.weekly_hours) | student | disabled | retired
        all_parents_eligible = (spm_unit.sum(parent) > 0) & (
            spm_unit.sum(parent & ~individually_eligible) == 0
        )
        homeless = spm_unit.household("is_homeless", period.this_year)
        # Follow other state CCDF models: callers can report that the family
        # satisfies an approved activity not individually modeled, including
        # qualifying parental leave, Pathway, training or protective services.
        # Pregnancy or PFML receipt alone does not establish this status.
        # The input is family-level, so setting it asserts that every parent
        # is covered; it cannot express the one-parent parental leave rule.
        other_activity = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_parents_eligible | homeless | other_activity
