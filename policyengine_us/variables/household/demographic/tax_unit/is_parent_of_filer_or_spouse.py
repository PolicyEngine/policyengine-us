from policyengine_us.model_api import *


class is_parent_of_filer_or_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is a parent"
    definition_period = YEAR
