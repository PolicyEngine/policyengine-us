from policyengine_us.model_api import *


class pr_actc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico additional child tax credit amount"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"
    defined_for = "pr_actc_eligibility"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.actc
        num_children = tax_unit("ctc_qualifying_children", period)
        
        credit_amt = num_children * p.amount # line 2
        modified_inc = tax_unit("pr_actc_modified_income_calculation", period) # lines 5-6
        ctc_amount = tax_unit("pr_ctc", period) # CTC + ODC amount, lines 7-9

        # earned income method to calculate credit amount
        # if modified agi > threshold -> minimum of the two amounts, lines 10 and 11
        # if modified agi < threshold -> original credit amount, line 5
        earned_inc_credit_amt = select(
            [
                modified_inc == 0,
                modified_inc != 0,
            ],
            [
                credit_amt,
                min(credit_amt, ctc_amount - modified_inc),
            ],
        )
        
        # another calculation of the credit through taxes paid
        taxes_paid = tax_unit("pr_actc_sum_taxes_paid", period) # lines 12a-14
        taxes_paid = taxes_paid - tax_unit("pr_additional_medicare_tax_withheld", period) # TODO - make me

        # line 15
        excess_ss_tax = tax_unit("pr_excess_social_security_withheld", period)

        # line 18
        ss_medicare_credit_amt = taxes_paid - excess_ss_tax

        # line 19
        return min(earned_inc_credit_amt, ss_medicare_credit_amt)