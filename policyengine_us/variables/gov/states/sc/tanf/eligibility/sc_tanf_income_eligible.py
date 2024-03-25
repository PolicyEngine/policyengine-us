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
        fpg = add(spm_unit, period, ["tax_unit_fpg"])
        # get need standard
        need_standard = fpg * p.need_standard.rate
        # get gross income limit
        gross_income_limit = need_standard * p.gross_income_limit
        # check eligible for income disregard
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        eligible_for_disregard = gross_earned_income <= gross_income_limit
        # get total net income and compare it with need standard
        total_net_income = spm_unit("sc_tanf_total_net_income", period)
        return (total_net_income < need_standard) & eligible_for_disregard
