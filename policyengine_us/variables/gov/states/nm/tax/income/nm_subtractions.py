from policyengine_us.model_api import *


class nm_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = [
        "tax_exempt_interest_income",  # Line 6
        "dividend_income",  # Line 6
        "us_govt_interest",  # Line 8
        "investment_in_529_plan",  # Line 14
        "military_service_income",  # Line 16, Line 19
    ]
