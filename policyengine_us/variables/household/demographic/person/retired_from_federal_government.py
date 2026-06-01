from policyengine_us.model_api import *


class retired_from_federal_government(Variable):
    value_type = bool
    entity = Person
    label = "Retired from Federal Government"
    definition_period = YEAR
    default_value = False
