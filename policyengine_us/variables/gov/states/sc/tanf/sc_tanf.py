from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "sc_tanf_eligible"
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf
        # Compute need standard based on ferderal poverty guidlines
        fpg = spm_unit("sc_tanf_fpg", period)
        need_standard = np.floor(fpg * p.income.need_standard.rate)
        # G
        total_net_income = spm_unit("sc_tanf_total_net_income", period)
        # I
        excess_income = need_standard - total_net_income
        return np.floor(excess_income * p.payment.rate)
