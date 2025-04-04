from policyengine_us.model_api import *


class pr_actc_modified_income_calculation(Variable):
    value_type = int
    entity = TaxUnit
    label = ""
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits
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
            modified_inc = modified_agi - threshold 
            # turn it into a multiple of 1000 if not already
            modified_inc = select(
                [(modified_inc % 1000 == 0), (modified_inc % 1000 != 0)], 
                [modified_inc, ((modified_inc // 1000) + 1) * 1000],
            ) * 0.05
        else:
            0
        
        return modified_inc