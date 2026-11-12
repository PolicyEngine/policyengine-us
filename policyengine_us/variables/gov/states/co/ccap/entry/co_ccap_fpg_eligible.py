from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)


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
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate monthly fpg limit, only for counties in Colorado.
        county = household("county_str", period.this_year)
        fpg_rate = np.zeros_like(county, dtype=float)
        mask = state_eligible
        if mask.any():
            valid_counties = np.array(list(p.entry.fpg_rate._children))
            lookup_county = np.where(
                np.isin(county, valid_counties),
                county,
                "DENVER_COUNTY_CO",
            )
            fpg_rate[mask] = p.entry.fpg_rate[lookup_county[mask]]
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = np.round(fpg * fpg_rate, 2)
        meets_income_limit = monthly_gross_income < fpg_limit
        return state_eligible & meets_income_limit
