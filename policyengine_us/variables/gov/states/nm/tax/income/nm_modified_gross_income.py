from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsfYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA"  # L    defined_for = StateCode.NM

    adds = [
        "tax_unit_social_security",
        "tax_unit_unemployment_compensation",
        "capital_gains",
        "tanf",
        "ssi",
        "interest_income",
        "dividend_income",
        "alimony_income",
        "child_support_received",
        "rent",
        "pension_income",
        "unemployment_compensation",
        "employment_income",
        # income such as gambling winnings, insurance settlements, scholarships,
        # grants, VA benefits, trust income and inheritance,
    ]
