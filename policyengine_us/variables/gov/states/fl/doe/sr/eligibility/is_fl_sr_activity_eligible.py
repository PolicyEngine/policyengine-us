from policyengine_us.model_api import *


class is_fl_sr_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.flsenate.gov/laws/statutes/2024/1002.81"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.doe.sr.eligibility
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        # A disabled parent is exempt from the activity requirement
        # (Fla. Stat. 1002.81(14) "working family"). The at-risk-child activity
        # pathway is not modeled at the moment.
        is_exempt = person("is_disabled", period.this_year)
        is_non_exempt_parent = is_parent & ~is_exempt
        non_exempt_parents = spm_unit.sum(is_non_exempt_parent)
        # Use pre-labor-supply-response hours so the work-activity test does not
        # move with the policy's own incentive effects (same convention as SNAP
        # work requirements, e.g. meets_snap_general_work_requirements).
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        combined_hours = spm_unit.sum(hours * is_non_exempt_parent)
        # Single non-exempt parent must work 20 hr/wk; two must work 40 hr/wk
        # combined. If every parent is exempt, the activity test is met.
        required_hours = where(
            non_exempt_parents > 1,
            p.activity_hours_two_parent,
            p.activity_hours_single,
        )
        # Fla. Stat. 1002.81(14) counts "eligible work OR education activities"
        # toward the 20/40 hours, and s. 1002.87(3) allows a job training or
        # educational program and a 90-day post-unemployment grace. PolicyEngine
        # derives only employment hours, so a family meeting the test through
        # education, job training, a work-transition program, or the grace
        # period sets meets_ccdf_activity_test (default false) as a fallback.
        # (The separate at-risk / protective-services priority is not modeled.)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (non_exempt_parents == 0) | (combined_hours >= required_hours) | fallback
