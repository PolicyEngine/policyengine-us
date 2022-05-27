from openfisca_us.model_api import *


class state_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "State taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        interest_dividend_income = add(
            tax_unit, period, ["interest_income", "dividend_income"]
        )
        agi_less_interest_dividend_income = agi - interest_dividend_income
        exemptions = tax_unit("state_income_tax_exemptions", period)
        deductions = tax_unit("state_income_tax_deductions", period)
        # Subtract and cap exemptions and deductions first, then add interest and dividends.
        capped_income_pre_interest_dividends = max_(
            agi_less_interest_dividend_income - exemptions - deductions, 0
        )
        return capped_income_pre_interest_dividends + interest_dividend_income
