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
            "pa_tanf_gross_unearned_income", period
        )

        # get the info: whether the person is full-time, and whether the person is disabled
        person = spm_unit.members
        is_full_time_eligible = spm_unit(
            "pa_tanf_personal_expense_full_time_eligible", period
        )
        is_disabled = person("is_ssi_disabled", period)

        # calculate earnings after EID(Earned Income Disregard) and WED(Work Expense Deduction) deduction
        p_eid_wed = parameters(
            period
        ).gov.states.pa.tanf.income.earned_deduction.earned_income_disregard

        p_pe = parameters(
            period
        ).gov.states.pa.tanf.income.earned_deduction.personal_expenses

        annual_flat_exclusion_eid = p_eid_wed.eid_flat * MONTHS_IN_YEAR
        annual_flat_exclusion_wed = p_eid_wed.wed_flat * MONTHS_IN_YEAR
        annual_deduction_full_time = (
            p_pe.maximum_deduction_full_time * MONTHS_IN_YEAR
        )
        annual_deduction_part_time = (
            p_pe.maximum_deduction_part_time * MONTHS_IN_YEAR
        )

        annual_gross_earnings = gross_earnings * MONTHS_IN_YEAR
        annual_gross_unearned_income = gross_unearned_income * MONTHS_IN_YEAR

        earnings_after_deduction_eid = max(
            annual_gross_earnings - annual_flat_exclusion_eid, 0
        ) * (1 - p_eid_wed.eid_percentage)
        earnings_after_deduction_eid_wed = max(
            earnings_after_deduction_eid - annual_flat_exclusion_wed, 0
        )

        # calculate earnings after personal expense deduction
        earnings_after_deduction_personal_expense = max(
            earnings_after_deduction_eid_wed
            - is_disabled
            * (
                is_full_time_eligible * annual_deduction_full_time
                + (1 - is_full_time_eligible) * annual_deduction_part_time
            ),
            0,
        )

        return (
            earnings_after_deduction_personal_expense
            + annual_gross_unearned_income
        )
