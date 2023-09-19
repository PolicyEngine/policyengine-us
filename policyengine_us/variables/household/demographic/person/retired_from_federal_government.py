from policyengine_us.model_api import *


class retired_from_federal_government(Variable):
    value_type = bool
    entity = Person
    label = "Retired from Federal Government"
    definition_period = YEAR
    defined_for = "is_retired"
    default_value = False
