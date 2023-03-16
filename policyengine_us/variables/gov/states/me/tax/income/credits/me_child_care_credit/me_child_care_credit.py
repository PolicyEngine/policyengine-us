from policyengine_us.model_api import *


class me_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME child care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf"  # (y)
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        placeholder = (
            0  # until I know how to define a new input for Step 4 Expenses
        )

        # Line 1: Total childcare expenses; record percentage of expenses that are regular vs. part of Step 4 child care program
        expenses = tax_unit("tax_unit_childcare_expenses", period)  # Line 1
        step_4_expenses = placeholder  # Line 1a, Column B
        regular_expenses = expenses - step_4_expenses  # Line 1a, Column A
        percentage_paid_regular = (
            regular_expenses / expenses
        )  # Line 1b, Column A
        percentage_paid_step_4 = (
            step_4_expenses / expenses
        )  # Line 1b, Column B

        # Line 2: Divide Federal CDCC according to share of regular vs. Step 4 expenses
        ctc = tax_unit(
            "cdcc", period
        )  # Line 2: credit for child and dependent care expenses from federal Form 1040 Schedule 3, Line 2, or Form 2441, line 11
        cdcc_regular_portion = (
            cdcc * percentage_paid_regular
        )  # Line 2a: Column A
        cdcc_step_4_portion = (
            cdcc * percentage_paid_step_4
        )  # Line 2a, Column B
        # p = parameters(period).gov.states.me.tax.income.credits.child_care

        # Line 3: Multiply CDCC regular and step 4 portion by associated factor to determine total Maine credit
        me_regular_child_care_credit = (
            0.25 * cdcc_regular_portion
        )  # Line 3, Column A
        me_step_4_child_care_credit = (
            0.5 * cdcc_step_4_portion
        )  # Line 3, Column B
        return me_regular_child_care_credit + me_step_4_child_care_credit
