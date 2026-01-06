from policyengine_us.model_api import *


class sc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        fpg = spm_unit("sc_tanf_fpg", period)
        # get need standard
        need_standard = np.floor(fpg * p.need_standard.rate)
        # get gross income limit
        gross_income_limit = np.floor(need_standard * p.gross_income_limit)
        # check eligibility for income disregard
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        eligible_for_disregard = gross_earned_income <= gross_income_limit
        # get total net income and compare it with need standard
        net_income = spm_unit("sc_tanf_net_income", period)
        income_eligible = net_income < need_standard
        return income_eligible & eligible_for_disregard
