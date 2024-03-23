from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = YEAR
    # defined_for = "sc_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income
        # A
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        # C
        fpg = add(spm_unit, period, ["tax_unit_fpg"])
        need_standard = fpg * p.need_standard.rate
        gross_income_limit = need_standard * p.gross_income_limit
        eligible_for_disregard = gross_earned_income <= gross_income_limit
        p_deduction = p.earned_income_deduction
        earned_income_after_disregard = max_(0,(
            gross_earned_income
            * p_deduction.percent
            * p_deduction.first_four_months
            / MONTHS_IN_YEAR
            + (gross_earned_income / MONTHS_IN_YEAR - p_deduction.amount)
            * (MONTHS_IN_YEAR - p_deduction.first_four_months)
        ))
        # D
        child_support = add(spm_unit, period, ["child_support_received"])
        net_earned_income = earned_income_after_disregard - child_support
        # G
        unearned_income = add(spm_unit, period, ["sc_tanf_unearned_income"])
        total_net_income = unearned_income + net_earned_income
        # I 
        p1 = parameters(period).gov.states.sc.tanf.payment
        tanf = (need_standard-total_net_income)*p1.rate/MONTHS_IN_YEAR
        return tanf

    