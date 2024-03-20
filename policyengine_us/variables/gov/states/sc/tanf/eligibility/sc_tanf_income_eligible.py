from policyengine_us.model_api import *


class sc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SC TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        gross_earned_income = add(spm_unit, period, "sc_tanf_earned_income")
        fpg = spm_unit("tax_unit_fpg", period)
        need_standard = fpg * p.need_standard.rate
        gross_income_limit = fpg * need_standard * p.gross_income_limit
        a = gross_earned_income <= gross_income_limit
        # apply 50% earned income disregard
        b = gross_earned_income * p.earned_income_deduction.percent
        c = b <= need_standard
        return a & c

        ##
        D: b - "child_support_paid_outside"
        F: sc_tanf_unearned_income - child_support_paid_remain
        G: F + D
        I: (need_standard - G) * p.payment.rate
