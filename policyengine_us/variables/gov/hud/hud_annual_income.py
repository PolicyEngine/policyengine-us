from policyengine_us.model_api import *


class hud_annual_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD annual income"
    unit = USD
    documentation = "Annual income for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.609"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hud
        person = spm_unit.members
        earned_income = person("hud_earned_income", period)
        unearned_income = person("hud_unearned_income", period)
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
        counted_person_income = (
            earned_income
            + unearned_income
            - child_earned_income_exclusion
            - student_earned_income_exclusion
        ) * is_family_member

        # TANF is a family benefit assigned to the unit, not an individual, so
        # it is counted whole and is not subject to the foster-member mask.
        return spm_unit.sum(counted_person_income) + spm_unit("tanf", period)
