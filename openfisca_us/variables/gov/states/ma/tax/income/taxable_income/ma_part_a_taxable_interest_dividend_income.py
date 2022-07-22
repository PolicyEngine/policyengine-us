from openfisca_us.model_api import *


class ma_part_a_taxable_interest_dividend_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A taxable income from interest or dividends"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_taxable_income = tax_unit("ma_part_a_taxable_income", period)
        interest_and_dividends = add(
            tax_unit, period, ["interest_income", "dividend_income"]
        )
        return min_(part_a_taxable_income, interest_and_dividends)
