from policyengine_us.model_api import *


class ssi_resource_test_seed(Variable):
    value_type = float
    entity = Person
    label = "Deterministic seed for SSI resource test"
    definition_period = YEAR
