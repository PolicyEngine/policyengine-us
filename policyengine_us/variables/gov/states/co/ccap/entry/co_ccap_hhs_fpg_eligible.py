from policyengine_us.model_api import *


class co_ccap_hhs_fpg_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Child Care Assistance Program through the household size federal poverty guidelines"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap
        monthly_agi = np.round(
            tax_unit("adjusted_gross_income", period) / MONTHS_IN_YEAR, 2
        )

        # Calculate monthly fpg limit
        county = tax_unit.household("county_str", period)
        hhs_fpg_rate = p.entry_fpg_rate[county]
        hhs_fpg = tax_unit("tax_unit_fpg", period)
        monthly_hhs_fpg = np.round(hhs_fpg * hhs_fpg_rate / MONTHS_IN_YEAR, 2)
        return monthly_agi < monthly_hhs_fpg
