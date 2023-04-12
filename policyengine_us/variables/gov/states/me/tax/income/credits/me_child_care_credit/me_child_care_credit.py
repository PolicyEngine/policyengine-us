from policyengine_us.model_api import *


class me_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME child care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.child_care

        # Get share of expenses that went to step 4 programs
        step_4_share_of_expenses = tax_unit(
            "me_step_4_share_of_child_care_expenses", period
        )
        # Line 2: Divide Federal CDCC according to share of regular vs. Step 4 expenses
        cdcc = tax_unit("cdcc", period)
        # Line 2a: Column A
        cdcc_regular_portion = cdcc * (1 - step_4_share_of_expenses)
        # Line 2a, Column B
        cdcc_step_4_portion = cdcc * step_4_share_of_expenses
        # Line 3, Column A
        me_regular_child_care_credit = (
            p.share_of_federal_credit.non_step_4 * cdcc_regular_portion
        )
        # Line 3, Column B
        me_step_4_child_care_credit = (
            p.share_of_federal_credit.step_4 * cdcc_step_4_portion
        )
        return me_regular_child_care_credit + me_step_4_child_care_credit
