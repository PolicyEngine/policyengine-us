from policyengine_us.model_api import *


class ca_tanf_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA