from policyengine_us.model_api import *


class co_ccap_hhs_smi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Colorado Child Care Assistance Program through the household size state median income"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
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
        # Calculate monthly smi limit
        hhs_smi_rate = p.entry.entry_hhs_smi_rate
        hhs_smi = spm_unit("snap_hhs_smi", period)
        monthly_hhs_smi = np.round(hhs_smi * hhs_smi_rate / MONTHS_IN_YEAR, 2)
        return monthly_gross_income < monthly_hhs_smi
