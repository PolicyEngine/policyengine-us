from policyengine_us.model_api import *


class pr_actc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico ACTC amount"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"
    defined_for = "pr_actc_eligibility"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.actc
        num_children = tax_unit("ctc_qualifying_children", period)

        # line 2
        base_actc_amount = num_children * p.amount
        # line 6
        inc_fraction = tax_unit("pr_actc_modified_income_fraction", period)
        # CTC + ODC amount, line 9
        ctc_amount = tax_unit("pr_ctc", period)

        # earned income method to calculate credit amount
        # if modified agi > threshold -> minimum of the two amounts, lines 10 and 11 (credit_amt_alt)
        # if modified agi < threshold -> original credit amount, line 5 (credit_amt)
        credit_amt_alt = min(base_actc_amount, ctc_amount - inc_fraction)
        earned_inc_credit_amt = select(
            [
                inc_fraction == 0,
                inc_fraction != 0,
            ],
            [
                base_actc_amount,
                credit_amt_alt,
            ],
        )

        # another calculation of the credit through taxes
        # lines 12a-14
        taxes_paid = tax_unit("pr_actc_sum_taxes_paid", period)
        # like a credit
        taxes_paid = taxes_paid - tax_unit(
            "pr_additional_medicare_tax_withheld", period
        )

        # line 15
        excess_ss_tax = tax_unit("pr_excess_social_security_withheld", period)

        # line 18
        ss_medicare_credit_amt = taxes_paid - excess_ss_tax

        # line 19
        return min_(earned_inc_credit_amt, ss_medicare_credit_amt)
