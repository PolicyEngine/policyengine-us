from policyengine_us.model_api import *


class ne_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("ne_taxable_income", period)
        p = parameters(period).gov.states.ne.tax.income.rates
        
        return select_filing_status_value(
            filing_status,
            p,
            taxable_income
        )
