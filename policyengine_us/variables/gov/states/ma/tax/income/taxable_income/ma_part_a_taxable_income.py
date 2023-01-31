from policyengine_us.model_api import *


class ma_part_a_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions"
    defined_for = StateCode.MA

    adds = [
        "ma_part_a_taxable_dividend_income",
        "ma_part_a_taxable_capital_gains_income",
    ]
