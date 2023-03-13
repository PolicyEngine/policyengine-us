from policyengine_us.model_api import *


class ca_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
        "https://www.ftb.ca.gov/forms/2022/2022-540.pdf"
    )
    defined_for = StateCode.CA
    adds = ["adjusted_gross_income", "ca_agi_additions"]
    subtracts = ["ca_agi_subtractions"]
