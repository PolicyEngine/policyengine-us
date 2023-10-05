from policyengine_us.model_api import *


class co_ccap_hhs_fpg_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Child Care Assistance Program through the household size federal poverty guidelines"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        spm_unit = tax_unit.spm_unit
        # state_code = spm_unit.household("state_code_str", period.this_year)
        monthly_agi = np.round(
            tax_unit("adjusted_gross_income", period.this_year) / MONTHS_IN_YEAR, 2
        )
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate monthly fpg limit
        county = tax_unit.household("county_str", period.this_year)
        hhs_fpg_rate = p.entry.entry_fpg_rate[county]
        hhs_fpg = spm_unit("snap_fpg", period)
        monthly_hhs_fpg = np.round(hhs_fpg * hhs_fpg_rate / MONTHS_IN_YEAR, 2)
        return monthly_agi < monthly_hhs_fpg
