from policyengine_us.model_api import *


class me_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine child care credit"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2",
    ]
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.child_care

        # Get share of expenses that went to step 4 programs
        step_4_share_of_expenses = tax_unit(
            "me_step_4_share_of_child_care_expenses", period
        )
        # Line 2: Divide Federal CDCC according to share of regular vs. Step 4 expenses
        # Maine matches the federal credit taken. 36 M.R.S. § 5218 sets the
        # credit at 25% of "the federal tax credit allowable for child and
        # dependent care expenses," and 36 M.R.S. § 111(1-A) fixes Maine's
        # "Code" at the IRC and amendments as of December 31, 2024. From 2026
        # that frozen Code excludes the OBBBA section 21 rate increase, so Maine
        # uses the pre-OBBBA federal credit.
        if period.start.year >= 2026:
            cdcc = tax_unit("pre_obbba_cdcc", period)
        else:
            cdcc = tax_unit("cdcc", period)
        # Line 2a: Column A
        cdcc_regular_portion = cdcc * (1 - step_4_share_of_expenses)
        # Line 2a, Column B
        cdcc_step_4_portion = cdcc * step_4_share_of_expenses
        # Line 3, Column A
        regular_child_care_credit = (
            p.share_of_federal_credit.non_step_4 * cdcc_regular_portion
        )
        # Line 3, Column B
        step_4_child_care_credit = (
            p.share_of_federal_credit.step_4 * cdcc_step_4_portion
        )
        return regular_child_care_credit + step_4_child_care_credit
