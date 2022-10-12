from policyengine_us.model_api import *


class ma_part_a_taxable_capital_gains_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A taxable income from capital gains"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_taxable_income = tax_unit("ma_part_a_taxable_income", period)
        part_a_taxable_interest_dividends = tax_unit(
            "ma_part_a_taxable_interest_dividend_income", period
        )
        return part_a_taxable_income - part_a_taxable_interest_dividends
