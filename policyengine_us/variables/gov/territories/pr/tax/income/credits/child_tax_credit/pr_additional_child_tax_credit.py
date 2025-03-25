from policyengine_us.model_api import *


class pr_additional_child_tax_credit(Variable):
    value_type = int
    entity = TaxUnit
    label = "Amount for Puerto Rico additional child tax credit"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits
        num_children = tax_unit("pr_child_tax_credit_number_eligible_children", period)
        other_dependents = 2 # TODO - calculate me
        # eligibility: 1+ children under 17
        if num_children < 1:
            return 0
        credit_amt = num_children * p.additional_child_tax_credit.amount
        modified_agi = 10_000 # TODO - need to calculate
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

        if modified_agi > threshold:
            # calculate phase-out
            mod_income = modified_agi - threshold
            if mod_income % 1000 != 0:
                mod_income = ((mod_income // 1000) + 1) * 1000 # turn it into a multiple of 1000
            mod_income = mod_income * 0.05
            mod_credit = num_children * 2000 + other_dependents * 500
            if mod_credit > mod_income:
                mod_credit = mod_credit - mod_income
                final_credit = min(credit_amt, mod_credit)
            else: 
                # CAN'T CLAIM CREDIT if mod_income > mod_credit
                return 0
        else:
            final_credit = credit_amt
        
        # sum up: self-employment tax + additional medicare tax on self-employment income + 13a-f 
        # (medicare tax, social security tax etc
        # sum - additional medicare tax withheld
        # total tax shouldn't be greater than sum, otherwise can't claim credit
        # otherwise, sum - total tax
        # final credit is min of final credit and sum - total tax (line 18)


        return credit_amt

