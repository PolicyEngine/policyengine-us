from policyengine_us.model_api import *


class sc_senior_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina senior exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf"
    defined_for = StateCode.SC

    adds = ["sc_senior_exemption_person"]
