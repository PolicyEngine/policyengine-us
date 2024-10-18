from policyengine_us.model_api import *


class preganant_expected_children(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = "The number of children a pregnant person is expecting"
    adds = ["is_pregnant"]
