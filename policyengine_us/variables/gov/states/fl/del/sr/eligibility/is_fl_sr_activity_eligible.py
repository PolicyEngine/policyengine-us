from policyengine_us.model_api import *


class is_fl_sr_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.flsenate.gov/laws/statutes/2024/1002.81"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl["del"].sr.eligibility
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        # A disabled parent is exempt from the activity requirement
        # (Fla. Stat. 1002.81(14) "working family"). The at-risk-child activity
        # pathway is not modeled at the moment.
        is_exempt = person("is_disabled", period.this_year)
        is_non_exempt_parent = is_parent & ~is_exempt
        non_exempt_parents = spm_unit.sum(is_non_exempt_parent)
        hours = person("weekly_hours_worked", period.this_year)
        combined_hours = spm_unit.sum(hours * is_non_exempt_parent)
        # Single non-exempt parent must work 20 hr/wk; two must work 40 hr/wk
        # combined. If every parent is exempt, the activity test is met.
        required_hours = where(
            non_exempt_parents > 1,
            p.activity_hours_two_parent,
            p.activity_hours_single,
        )
        return (non_exempt_parents == 0) | (combined_hours >= required_hours)
