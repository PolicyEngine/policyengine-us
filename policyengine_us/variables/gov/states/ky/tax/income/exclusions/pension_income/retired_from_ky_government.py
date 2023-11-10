from policyengine_us.model_api import *


class retired_from_ky_government(Variable):
    value_type = bool
    entity = Person
    label = "Retired from state or local government in Kentucky"
    definition_period = YEAR
    defined_for = StateCode.KY
    default_value = False
