from policyengine_us.model_api import *


class il_tanf_countable_income_at_application(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable income at application"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.tanf.income.initial_employment_deduction

        countable_gross_earned_income = spm_unit(
            "il_tanf_countable_gross_earned_income", period
        )
        childcare_deduction = spm_unit("il_tanf_childcare_deduction", period)
        adjusted_earned_income = max_(
            countable_gross_earned_income - childcare_deduction, 0
        )
        fpg = spm_unit("spm_unit_fpg", period)
        payment_level = spm_unit("il_tanf_payment_level", period)
        # Create a new variable for IED
        initial_employment_deduction_person = p.rate * fpg - payment_level
        is_employed = (
            spm_unit.members("il_tanf_gross_earned_income", period) > 0
        )
        is_head_or_spouse = spm_unit.members(
            "is_tax_unit_head_or_spouse", period
        )
        ied_eligible_person = is_employed & is_head_or_spouse
        initial_employment_deduction = (
            ied_eligible_person * initial_employment_deduction_person
        )

        earned_income_deduction = min_(
            adjusted_earned_income, initial_employment_deduction
        )
        countable_unearned_income = spm_unit(
            "il_tanf_countable_unearned_income", period
        )

        return (
            adjusted_earned_income
            - earned_income_deduction
            + countable_unearned_income
        )
