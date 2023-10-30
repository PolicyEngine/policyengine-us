from policyengine_us.model_api import *


class co_ccap_re_determination_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the re-determination of Colorado Child Care Assistance Program through income"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        monthly_agi = np.round(
            tax_unit("adjusted_gross_income", period.this_year)
            / MONTHS_IN_YEAR,
            2,
        )
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate monthly smi limit
        hhs_smi_rate = p.re_determination.re_determination_hhs_smi_rate
        hhs_smi = tax_unit.spm_unit("snap_hhs_smi", period)
        monthly_hhs_smi = np.round(hhs_smi * hhs_smi_rate / MONTHS_IN_YEAR, 2)
        return monthly_agi < monthly_hhs_smi
