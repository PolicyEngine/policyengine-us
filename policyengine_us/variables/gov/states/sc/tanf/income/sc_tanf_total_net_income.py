from policyengine_us.model_api import *


class sc_tanf_total_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF total net income"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dss.sc.gov/media/3926/tanf_policy_manual_vol-60.pdf#page=131"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.tanf.income.earned.disregard
        # A
        gross_earned_income = add(spm_unit, period, ["sc_tanf_earned_income"])
        # C Compute earned income after disregard, first four months has 50% disregard, the rest has $100 deduction.
        first_four_months_income = (
            gross_earned_income
            * p.percent
            * p.first_four_months
            / MONTHS_IN_YEAR
        )
        rest_of_the_months = max_(MONTHS_IN_YEAR - p.first_four_months, 0)
        rest_months_income = max_(
            gross_earned_income / MONTHS_IN_YEAR - p.amount, 0
        )
        remaining_income =  rest_months_income * rest_of_the_months  
        earned_income_after_disregard = max_(  
            0,  
            (  
                first_four_months_income  
                + remaining_income  
            ),  
        )  
        # D
        child_support = add(spm_unit, period, ["child_support_received"])
        net_earned_income = max_(
            earned_income_after_disregard - child_support, 0
        )
        # G
        unearned_income = add(spm_unit, period, ["sc_tanf_unearned_income"])
        total_net_income = unearned_income + net_earned_income
        return np.round(total_net_income, 0)
