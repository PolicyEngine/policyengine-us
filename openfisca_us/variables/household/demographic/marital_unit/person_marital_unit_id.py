from policyengine_us.model_api import *


class person_marital_unit_id(Variable):
    value_type = int
    entity = Person
    label = "Marital unit ID"
    definition_period = YEAR
