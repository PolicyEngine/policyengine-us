from policyengine_us.model_api import *


class pr_additional_child_tax_credit(Variable):
    value_type = int
    entity = TaxUnit
    label = "Amount for Puerto Rico additional child tax credit"
    definition_period = YEAR
    reference = ""
    defined_for = "pr_additional_child_tax_credit_eligibility"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits
        num_children = tax_unit("pr_child_tax_credit_number_eligible_children", period)
        other_dependents = tax_unit("tax_unit_dependents") - num_children
        
        credit_amt = num_children * p.additional_child_tax_credit.amount
        modified_agi = tax_unit("pr_modified_agi", period)
        modified_inc = tax_unit("pr_actc_modified_income_calculation", period) # if 0, modified_agi under threshold
        income_threshold = num_children * 2000 + other_dependents * 500 # threshold

        # earned income method to calculate credit amount
        earned_inc_credit_amt = select(
            [
                modified_inc == 0,
                modified_inc != 0,
            ],
            [
                credit_amt,
                min(credit_amt, income_threshold - modified_inc),
            ],
        )

        
        # calculate an alternate way for the credit amount through social security & medicare tax paid
        # use the smaller method as the final amount for the credit
        person = tax_unit.members
        taxes_paid = 0.5 * person("self_employment_tax", period) + 0.5 * tax_unit("additional_medicare_tax", period) + tax_unit("pr_withheld_income", period)
        # subtract additional medicare tax on medicare wages from Form 8959

        # excess social security tax withheld
        excess_ss_tax = tax_unit("excess_social_security_withheld", period) # TODO - create a variable for me
        if excess_ss_tax > taxes_paid:
            # CAN'T CLAIM THE CREDIT
            return 0
        else: 
            ss_medicare_credit_amt = taxes_paid - excess_ss_tax

        return min(earned_inc_credit_amt, ss_medicare_credit_amt)