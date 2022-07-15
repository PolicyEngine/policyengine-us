from openfisca_us.model_api import *


class mo_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-A_2021.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        threshold = parameters(period).gov.states.mo.tax.income.mo_taxable_income.mo_federal_itemization_threshold[filing_status]

        #any itemizations 
        agi = tax_unit("adjusted_gross_income", period)
        total_itemized_federal_deductions = tax_unit("mo_federal_itemized_deductions", period)
        if total_itemized_federal_deductions > 0:
            
            person = tax_unit.members
            social_security_tax = person("employee_social_security_tax", period)
            medicare_tax = person("employee_medicare_tax", period)
            self_employment_tax = person("self_employment_tax", period)
            items = (total_itemized_federal_deductions + social_security_tax + medicare_tax + self_employment_tax)
            
            #taxes/income
            state_and_local_sales_or_income_tax = tax_unit("state_and_local_sales_or_income_tax", period)
            net_state_income_taxes = state_and_local_sales_or_income_tax - self_employment_tax

            #itemizations from federal return w/ > $10,000 or $5,000 (MFS) in state and local taxes
            if state_and_local_sales_or_income_tax > threshold:
                real_estate_tax = tax_unit("real_estate_taxes", period)
                base_amount = parameters(period).gov.states.mo.tax.income.mo_taxable_income.mo_salt_cap[filing_status]
                #overwrites the net_state_income_taxes variable assigned above
                adjustment = base_amount * (real_estate_tax / (state_and_local_sales_or_income_tax - self_employment_tax))
                net_state_income_taxes = state_and_local_sales_or_income_tax - adjustment
                return agi - (items - net_state_income_taxes)
            else:
                return agi - (items - net_state_income_taxes)
        else:
            return agi
