from policyengine_us.model_api import *


class ma_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_interest_dividends = tax_unit(
            "ma_part_a_taxable_interest_dividend_income", period
        )
        part_a_capital_gains = tax_unit(
            "ma_part_a_taxable_capital_gains_income", period
        )
        part_b = tax_unit("ma_part_b_taxable_income", period)
        part_c = tax_unit("ma_part_c_taxable_income", period)
        rates = parameters(period).gov.states.ma.tax.income.rates
        exempt = tax_unit("is_ma_income_tax_exempt", period)
        tax_on_income = (
            rates.part_a_interest_dividends * part_a_interest_dividends
            + rates.part_a_capital_gains * part_a_capital_gains
            + rates.part_b * part_b
            + rates.part_c * part_c
        )
        return ~exempt * tax_on_income
