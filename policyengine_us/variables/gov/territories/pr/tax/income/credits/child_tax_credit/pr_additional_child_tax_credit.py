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
        other_dependents = 2 # TODO - calculate me
        
        credit_amt = num_children * p.additional_child_tax_credit.amount
        modified_agi = tax_unit("pr_modified_agi", period)
        filing_status = tax_unit("filing_status", period)

        threshold = select(
            [
                filing_status == filing_status.possible_values.JOINT,
                filing_status != filing_status.possible_values.JOINT,
            ],
            [
                p.child_tax_credit.income_limit_joint,
                p.child_tax_credit.income_limit_single,
            ],
        )

        # earned income method to calculate credit amount
        if modified_agi > threshold:
            # calculate phase-out 
            # calculate credit based on income earned over the threshold
            inc_credit = modified_agi - threshold 
            # turn it into a multiple of 1000 if not already
            inc_credit = select(
                [(inc_credit % 1000 == 0), (inc_credit % 1000 != 0)], 
                [inc_credit, ((inc_credit // 1000) + 1) * 1000],
            ) * 0.05

            base_credit = num_children * 2000 + other_dependents * 500
            # credit is limited based on income
            if base_credit > inc_credit:
                base_credit = base_credit - inc_credit
                final_credit = min(credit_amt, base_credit)
            else: 
                # CAN'T CLAIM CREDIT if inc_credit > base_credit
                return 0
        else:
            # otherwise if modified agi under threshold, stick with initial
            # computation of the credit
            final_credit = credit_amt
        
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

        return min(final_credit, ss_medicare_credit_amt)