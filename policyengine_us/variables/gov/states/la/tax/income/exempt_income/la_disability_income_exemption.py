from policyengine_us.model_api import *


class la_disability_income_exemption(Variable):
    value_type = float
    entity = Person
    label = "Louisiana disability income exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"  # (B)
    defined_for = StateCode.LA

    adds = ["la_disability_income_exemption_person"]
