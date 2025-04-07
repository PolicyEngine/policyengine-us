from policyengine_us.model_api import *


class ca_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    defined_for = StateCode.CA
