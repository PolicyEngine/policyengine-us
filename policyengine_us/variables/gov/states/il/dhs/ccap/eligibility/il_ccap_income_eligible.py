from policyengine_us.model_api import *


class il_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Child Care Assistance Program (CCAP) due to income"
    definition_period = MONTH
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=118832",
        "https://www.illinois.gov/content/dam/soi/en/web/illinois/iisnewsattachments/20670-pritzker-administration-announces-expanded-child-care-assistance-program.pdf#page=1",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.income.income_limit
        countable_income = spm_unit("il_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        smi = spm_unit("hhs_smi", period)
        enrolled_in_ccap = spm_unit("il_ccap_enrolled", period)
        initial_rate = p.new_applicants_rate
        if p.initial_2019.in_effect:
            initial_rate = p.initial_2019.rate
        initial_income_limit = initial_rate * fpg
        redetermination_income_limit = p.redetermination_rate * fpg
        phase_out_income_limit = p.smi_rate * smi
        continuing_income_limit = max_(
            phase_out_income_limit,
            redetermination_income_limit,
        )
        income_limit = where(
            enrolled_in_ccap,
            continuing_income_limit,
            initial_income_limit,
        )
        return countable_income <= income_limit
