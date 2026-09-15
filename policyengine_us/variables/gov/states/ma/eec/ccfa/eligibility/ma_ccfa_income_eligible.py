from policyengine_us.model_api import *


class ma_ccfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=36",
        "https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.income
        person = spm_unit.members
        eligible_child = person("ma_ccfa_eligible_child", period)
        disabled_child = spm_unit.any(
            eligible_child & person("is_disabled", period.this_year)
        )
        initial_limit = where(
            disabled_child,
            max_(p.smi_rate.new_applicants, p.smi_rate.disabled_child),
            p.smi_rate.new_applicants,
        )
        smi_rate = where(
            spm_unit("ma_ccfa_enrolled", period),
            p.smi_rate.redetermination,
            initial_limit,
        )
        eligible = (
            spm_unit("ma_ccfa_countable_income", period)
            <= spm_unit("hhs_smi", period) * smi_rate
        )
        if p.homeless_exemption_in_effect:
            eligible |= spm_unit.household("is_homeless", period.this_year)
        return eligible
