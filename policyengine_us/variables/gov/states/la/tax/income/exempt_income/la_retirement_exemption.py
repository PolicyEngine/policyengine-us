from policyengine_us.model_api import *


class la_retirement_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana retirement exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA

    adds = ["la_retirement_exemption_person"]
