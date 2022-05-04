from openfisca_us.model_api import *


class gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Gross income"
    unit = USD
    documentation = "Gross income, as defined in the Internal Revenue Code"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/61"

    formula = sum_of_variables([
        "tax_unit_employment_income",
        "tax_unit_salt_refund_income",
        "tax_unit_alimony_income",
        "tax_unit_business_income",
        "tax_unit_taxable_ira_income",
        "tax_unit_farm_income",
        "tax_unit_unemployment_insurance",
        "tax_unit_interest_income",
        "tax_unit_ordinary_dividend_income",
        "tax_unit_net_capital_gains",
        "tax_unit_non_schedule_d_capital_gains",
        "tax_unit_other_net_gain",
    ])
