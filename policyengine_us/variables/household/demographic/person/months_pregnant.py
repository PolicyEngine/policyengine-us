from policyengine_us.model_api import *


class months_pregnant(Variable):
    value_type = int
    entity = Person
    label = "Number of pregnancy months completed"
    definition_period = YEAR
