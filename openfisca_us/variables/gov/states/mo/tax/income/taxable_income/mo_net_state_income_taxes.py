from openfisca_us.model_api import *


class mo_net_state_income_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri net state income taxes"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        adjustment_base_amount = parameters(period).gov.states.mo.tax.income.taxable_income.salt_cap[filing_status]
        
        #taxes/income
        state_and_local_sales_or_income_tax = tax_unit("state_and_local_sales_or_income_tax", period)
        state_and_local_income_tax = add(tax_unit, period, ["state_income_tax", "local_income_tax"])
        earnings_tax = tax_unit("local_income_tax", period) #defined as local income tax from the Federal W2 on page 26 of MO-1040 2021
        
        net_state_income_taxes = state_and_local_income_tax - earnings_tax
        income_tax_to_total_ratio = net_state_income_taxes/state_and_local_sales_or_income_tax
        #the threshold is the same as the adjustment_base_amount
        threshold = adjustment_base_amount

        return where(state_and_local_sales_or_income_tax > threshold ,adjustment_base_amount * (income_tax_to_total_ratio), net_state_income_taxes)
