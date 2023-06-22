from policyengine_us.model_api import *


class pa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "PA TANF countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit("pa_tanf_gross_earned_income", period)
        gross_unearned_income = spm_unit(
            "pa_tanf_countable_gross_unearned_income", period
        )

        p_eid_wed = parameters(
            period
        ).gov.states.pa.tanf.income.earned_deduction.earned_income_disregard_and_work_expense_deduction
        annual_flat_exclusion_eid = p_eid_wed.eid_flat * MONTHS_IN_YEAR
        earnings_after_deduction_eid = max_(
            gross_earnings - annual_flat_exclusion_eid, 0
        ) * (1 - p_eid_wed.eid_percentage)
        earnings_after_deduction_eid_wed = max(
            earnings_after_deduction_eid - p_eid_wed.wed_flat, 0
        )

        p_pe = parameters(
            period
        ).gov.states.pa.tanf.income.earned_deduction.personal_expenses

        earnings_after_deduction_personal_expense = is_ssi_disabled * (
            is_full_time_employment * p_pe.maximum_deduction_full_time
            + (1 - is_full_time_employment) * p_pe.maximum_deduction_part_time
        )

        return (
            earnings_after_deduction_eid_wed
            + earnings_after_deduction_personal_expense
            + gross_unearned_income
        )
