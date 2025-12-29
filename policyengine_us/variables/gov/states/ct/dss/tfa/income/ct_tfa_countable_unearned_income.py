from policyengine_us.model_api import *


class ct_tfa_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.income.deduction
        total_unearned_income = add(
            spm_unit, period, ["tanf_gross_unearned_income"]
        )
        # Get child support - PolicyEngine handles period conversion automatically
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_deduction = min_(child_support, p.child_support)

        return max_(0, total_unearned_income - child_support_deduction)
