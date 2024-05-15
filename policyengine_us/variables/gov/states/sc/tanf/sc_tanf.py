from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "sc_tanf_eligible"
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf
        # Compute need standard based on ferderal poverty guidlines
        fpg = spm_unit("sc_tanf_fpg", period)
        need_standard = fpg * p.income.need_standard.rate
        net_income = spm_unit("sc_tanf_net_income", period)
        excess_income = need_standard - net_income
        return excess_income * p.payment.rate
