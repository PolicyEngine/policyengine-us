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
        sources = p.annual_income.sources
        earned_income_sources = sources.earned
        unearned_income_sources = sources.unearned

        income = add(spm_unit, period, earned_income_sources) + add(
            spm_unit, period, unearned_income_sources
        )
        earned_income = sum(
            spm_unit.members(source, period) for source in earned_income_sources
        )
        positive_earned_income = max_(earned_income, 0)

        is_child = spm_unit.members("is_child", period)
        child_earned_income_exclusion = positive_earned_income * is_child

        dependent_full_time_student = (
            spm_unit.members("is_tax_unit_dependent", period)
            & spm_unit.members("is_full_time_student", period)
            & ~is_child
        )
        dependent_deduction = p.adjusted_income.deductions.dependent.amount
        student_earned_income_exclusion = (
            max_(positive_earned_income - dependent_deduction, 0)
            * dependent_full_time_student
        )

        return income - spm_unit.sum(
            child_earned_income_exclusion + student_earned_income_exclusion
        )
