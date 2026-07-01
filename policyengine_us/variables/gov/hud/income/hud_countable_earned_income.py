from policyengine_us.model_api import *


class hud_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD countable earned income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.609"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hud
        person = spm_unit.members
        earned_income = person("hud_earned_income", period)
        positive_earned_income = max_(earned_income, 0)

        is_child = person("is_child", period)
        child_earned_income_exclusion = positive_earned_income * is_child

        dependent_full_time_student = (
            person("is_hud_dependent", period)
            & person("is_full_time_student", period)
            & ~is_child
        )
        dependent_deduction = p.adjusted_income.deductions.dependent.amount
        student_earned_income_exclusion = (
            max_(positive_earned_income - dependent_deduction, 0)
            * dependent_full_time_student
        )

        # Foster children and adults are not family members (24 CFR 5.603), so
        # their own income does not count.
        is_family_member = ~person("is_in_foster_care", period)
        return spm_unit.sum(
            (
                earned_income
                - child_earned_income_exclusion
                - student_earned_income_exclusion
            )
            * is_family_member
        )
