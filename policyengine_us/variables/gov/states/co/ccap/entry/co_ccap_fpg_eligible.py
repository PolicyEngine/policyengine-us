from policyengine_us.model_api import *


class co_ccap_fpg_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Colorado Child Care Assistance Program poverty-based income eligibility test"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19"
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        household = spm_unit.household
        state_eligible = household("state_code_str", period.this_year) == "CO"
        monthly_gross_income = np.round(
            spm_unit("co_ccap_countable_income", period),
            2,
        )
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate monthly fpg limit, only for counties in Colorado.
        county = household("county_str", period.this_year)
        fpg_rate = np.zeros_like(county, dtype=float)
        mask = state_eligible

        # Current fix for counties not in the dataset.
        try:
            p.entry.fpg_rate[county[mask]]
        except:
            county = np.array(
                ["DENVER_COUNTY_CO"] * len(county),
            )
        if mask.any():
            fpg_rate[mask] = p.entry.fpg_rate[county[mask]]
        # SNAP FPG is monthly.
        fpg = spm_unit("snap_fpg", period)
        fpg_limit = np.round(fpg * fpg_rate, 2)
        meets_income_limit = monthly_gross_income < fpg_limit
        return state_eligible & meets_income_limit
