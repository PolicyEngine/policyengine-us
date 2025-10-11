from policyengine_us.model_api import *


class co_ccap_re_determination_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the re-determination of Colorado Child Care Assistance Program through income"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19"
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
        smi = spm_unit("hhs_smi", period.this_year) / MONTHS_IN_YEAR
        income_limit = np.round(smi * p.re_determination.smi_rate, 2)
        return monthly_gross_income < income_limit
