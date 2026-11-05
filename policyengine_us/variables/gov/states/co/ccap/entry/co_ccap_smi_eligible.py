from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)


class co_ccap_smi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Colorado Child Care Assistance Program state median income-based income eligibility test"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19"
    definition_period = MONTH
    # defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        monthly_gross_income = np.round(
            spm_unit("co_ccap_countable_income", period),
            2,
        )
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap
        # Calculate monthly smi limit
        smi = spm_unit("co_ccap_smi", period)
        income_limit = np.round(smi * p.entry.smi_rate, 2)
        return monthly_gross_income < income_limit
