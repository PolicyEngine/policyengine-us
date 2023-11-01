from policyengine_us.model_api import *


class co_ccap_hhs_fpg_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Colorado Child Care Assistance Program through the household size federal poverty guidelines"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        state_eligible = (
            spm_unit.household("state_code_str", period.this_year) == "CO"
        )
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
        county = spm_unit.household("county_str", period.this_year)
        hhs_fpg_rate = np.zeros_like(county, dtype=float)
        mask = state_eligible
        if hasattr(spm_unit.simulation, "dataset"):
            county = np.array(
                ["DENVER_COUNTY_CO"] * len(county),
            )
        if mask.any():
            hhs_fpg_rate[mask] = p.entry.entry_fpg_rate[county[mask]]
        hhs_fpg = spm_unit("snap_fpg", period)
        monthly_hhs_fpg = np.round(hhs_fpg * hhs_fpg_rate / MONTHS_IN_YEAR, 2)
        meets_income_limit = monthly_gross_income < monthly_hhs_fpg
        return state_eligible & meets_income_limit
