from policyengine_us.model_api import *


class pr_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico charitable deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=5"
    defined_for = StateCode.PR
    
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.taxable_income.deductions.charity
        # sum up charitable contributions - line 1, column B
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(
            tax_unit, period, ["charitable_non_cash_donations"]
        )
        charitable_sum = cash_donations + non_cash_donations

        # 50% of AGI is the maximum deduction for charitable contributions, line 4
        charity_floor = p.floor * tax_unit("pr_agi", period)
        # line 5
        return min_(charitable_sum, charity_floor)
        
        
