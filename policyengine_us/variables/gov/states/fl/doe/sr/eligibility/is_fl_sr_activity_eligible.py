from policyengine_us.model_api import *


class is_fl_sr_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.flsenate.gov/laws/statutes/2025/1002.81"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.doe.sr.eligibility
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use pre-labor-supply-response hours so the work-activity test does not
        # move with the policy's own incentive effects (same convention as SNAP
        # work requirements, e.g. meets_snap_general_work_requirements).
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        # A parent exempt from the work requirement due to disability
        # (Fla. Stat. 1002.81(14)(c)). The statute also allows an age exemption,
        # which -- like other approved non-work activities -- is reachable via
        # meets_ccdf_activity_test below.
        is_disabled = person("is_disabled", period.this_year)

        n_parents = spm_unit.sum(is_parent)
        n_exempt = spm_unit.sum(is_parent & is_disabled)
        # Parent meeting the individual 20-hour/week bar.
        meets_individual = is_parent & (hours >= p.activity_hours_single)
        n_meeting_individual = spm_unit.sum(meets_individual)
        n_nonexempt_meeting = spm_unit.sum(meets_individual & ~is_disabled)
        combined_parent_hours = spm_unit.sum(hours * is_parent)

        # Fla. Stat. 1002.81(14) "working family":
        # (a) single-parent family -- the parent works >= 20 hr/wk. There is no
        #     disability exemption for a single parent (the exemption in (c)
        #     applies only to two-parent families).
        single_ok = (n_parents == 1) & (n_meeting_individual >= 1)
        # (b) two-parent family, neither parent exempt -- combined >= 40 hr/wk.
        two_parent_ok = (
            (n_parents >= 2)
            & (n_exempt == 0)
            & (combined_parent_hours >= p.activity_hours_two_parent)
        )
        # (c) two-parent family, one parent exempt due to age/disability -- the
        #     other (non-exempt) parent works >= 20 hr/wk. If both parents are
        #     exempt, there is no working parent and the family does not qualify.
        exemption_ok = (n_parents >= 2) & (n_exempt >= 1) & (n_nonexempt_meeting >= 1)
        # 1002.81(14) counts "eligible work OR education activities" and
        # s. 1002.87(3) allows a job training/educational program and a 90-day
        # post-unemployment grace -- activities PolicyEngine can't derive from
        # employment hours, so meets_ccdf_activity_test (default false) is an
        # OR-fallback. (The separate at-risk / protective-services priority is
        # not modeled.)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return single_ok | two_parent_ok | exemption_ok | fallback
