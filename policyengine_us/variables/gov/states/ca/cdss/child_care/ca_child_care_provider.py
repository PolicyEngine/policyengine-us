from policyengine_us.model_api import *


class ca_child_care_provider(Variable):
    value_type = str
    entity = SPMUnit
    label = "California CalWORKs Child Care Provider"
    definition_period = YEAR
    defined_for = StateCode.CA
