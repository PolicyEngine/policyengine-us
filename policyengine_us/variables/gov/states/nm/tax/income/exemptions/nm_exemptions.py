from policyengine_us.model_api import *


class nm_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = [
        "nm_aged_blind_exemption",
        "nm_hundred_year_exemption",
        "nm_low_and_middle_income_exemption",
        "nm_medical_expense_exemption",
        "nm_social_security_income_exemption",
    ]
