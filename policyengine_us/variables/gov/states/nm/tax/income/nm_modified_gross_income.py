from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = [
        "employment_income",
        "tax_unit_social_security",
        "tax_unit_unemployment_compensation",
        "capital_gains",
        "tanf",
        "ssi",
        "interest_income",
        "dividend_income"
        # income such as interest, dividends, gambling winnings, insurance settlements, scholarships,
        # grants, VA benefits, trust income and inheritance, alimony, and child support
    ]
