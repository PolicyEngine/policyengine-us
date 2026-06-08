from policyengine_us.model_api import *


class is_fl_sr_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://flrules.elaws.us/fac/6m-4.200",
        "https://www.flsenate.gov/laws/statutes/2024/1002.81",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl["del"].sr
        if not p.in_effect:
            return False
        has_eligible_child = add(spm_unit, period, ["is_fl_sr_child_eligible"]) > 0
        income_eligible = spm_unit("is_fl_sr_income_eligible", period)
        activity_eligible = spm_unit("is_fl_sr_activity_eligible", period)
        # Florida's $1,000,000 self-certified asset limit matches the federal
        # CCDF asset ceiling, so reuse the federal check.
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        return has_eligible_child & income_eligible & activity_eligible & asset_eligible
