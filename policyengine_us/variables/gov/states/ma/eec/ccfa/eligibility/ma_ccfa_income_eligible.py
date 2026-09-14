from policyengine_us.model_api import *


class ma_ccfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/financial-assistance-policy-guide"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.income.smi_rate

        countable_income = spm_unit("ma_ccfa_countable_income", period)
        smi = spm_unit("hhs_smi", period)

        is_enrolled = spm_unit("ma_ccfa_enrolled", period)

        if p.disabled_child_exception:
            person = spm_unit.members
            disabled_child = person("ma_ccfa_eligible_child", period) & person(
                "is_disabled", period.this_year
            )
            is_enrolled = is_enrolled | spm_unit.any(disabled_child)

        smi_limit = where(
            is_enrolled,
            p.redetermination,
            p.new_applicants,
        )
        income_limit = smi * smi_limit
        eligible = countable_income <= income_limit
        ccfa = parameters(period).gov.states.ma.eec.ccfa
        if ccfa.homeless_income_and_copay_exempt:
            eligible = eligible | spm_unit.household("is_homeless", period.this_year)
        return eligible
