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
        p = parameters(period).gov.states.me.tax.income.credits.child_care

        # Line 1: Total childcare expenses; record percentage of expenses that are regular vs. part of Step 4 child care program
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        # Line 1a, Column B
        step = tax_unit("me_step", period)
        step_4_expenses = max(step - 3, 0) * tax_unit(
            "me_child_care_step_expenses", period
        )  # step 4 expenses only qualify
        # Line 1a, Column A
        regular_expenses = expenses - step_4_expenses
        # Line 1b, Column A
        percentage_paid_regular = np.nan_to_num(regular_expenses / expenses)
        # Line 1b, Column B
        percentage_paid_step_4 = np.nan_to_num(step_4_expenses / expenses)
        # Line 2: Divide Federal CDCC according to share of regular vs. Step 4 expenses
        cdcc = tax_unit("cdcc", period)
        # Line 2a: Column A
        cdcc_regular_portion = cdcc * percentage_paid_regular
        # Line 2a, Column B
        cdcc_step_4_portion = cdcc * percentage_paid_step_4
        # Line 3, Column A
        me_regular_child_care_credit = (
            p.regular_share_of_federal_credit * cdcc_regular_portion
        )
        # Line 3, Column B
        me_step_4_child_care_credit = (
            p.step_4_share_of_federal_credit * cdcc_step_4_portion
        )
        return me_regular_child_care_credit + me_step_4_child_care_credit
