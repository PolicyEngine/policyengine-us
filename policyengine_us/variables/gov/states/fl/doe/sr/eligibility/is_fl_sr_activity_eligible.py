from policyengine_us.model_api import *


class is_fl_sr_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.flsenate.gov/laws/statutes/2025/1002.81"

    def formula(spm_unit, period, parameters):
        # School Readiness activity requirement, modeled exactly as Fla. Stat.
        # 1002.81(14) "working family" (confirmed by the FFY2025-27 CCDF State
        # Plan s. 2.2.2):
        #   (a) single-parent family: the parent works >= 20 hr/wk;
        #   (b) two-parent family, neither exempt: combined >= 40 hr/wk;
        #   (c) two-parent family with one parent exempt from work due to age or
        #       disability: the OTHER parent works >= 20 hr/wk.
        # The age/disability exemption is two-parent-only (c). A single parent
        # who cannot work due to age/disability, a both-exempt couple, or any
        # other approved non-work activity (job search/education/training, the
        # 90-day post-unemployment grace per s. 1002.87(3), or a protective-
        # services determination) is not derivable from employment hours and is
        # captured via meets_ccdf_activity_test below.
        p = parameters(period).gov.states.fl.doe.sr.eligibility
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        # Pre-labor-supply-response hours, so the test does not move with the
        # policy's own incentive effects (SNAP work-requirement convention).
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        # Exempt from work due to age or disability under 1002.81(14)(c).
        # Disability uses is_disabled; age uses the repository-wide senior flag
        # as an approximation. A documented exemption outside these proxies is
        # reachable via meets_ccdf_activity_test.
        is_exempt = person("is_disabled", period.this_year) | person(
            "is_senior", period.this_year
        )
        n_parents = spm_unit.sum(is_parent)
        n_exempt = spm_unit.sum(is_parent & is_exempt)
        # A parent meeting the individual 20-hour/week bar...
        meets_individual = is_parent & (hours >= p.activity_hours_single)
        # ...and a NON-exempt parent meeting it (the working parent in case (c)).
        n_nonexempt_meeting = spm_unit.sum(meets_individual & ~is_exempt)
        combined_parent_hours = spm_unit.sum(hours * is_parent)

        # (a) single parent works >= 20 (no single-parent exemption).
        single_ok = (n_parents == 1) & (spm_unit.sum(meets_individual) >= 1)
        # (b) two-parent, neither exempt: combined >= 40.
        two_parent_ok = (
            (n_parents >= 2)
            & (n_exempt == 0)
            & (combined_parent_hours >= p.activity_hours_two_parent)
        )
        # (c) two-parent, one parent exempt (age/disability) + the other works
        #     >= 20. A both-exempt couple does not qualify (no working parent).
        exemption_ok = (n_parents >= 2) & (n_exempt >= 1) & (n_nonexempt_meeting >= 1)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return single_ok | two_parent_ok | exemption_ok | fallback
