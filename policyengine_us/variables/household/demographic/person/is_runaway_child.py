from policyengine_us.model_api import *


class is_runaway_child(Variable):
    value_type = bool
    entity = Person
    label = "Is runaway child"
    documentation = "Whether an individual under 18 years old leaves home or their legal residence without parental or guardian permission"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/34/11279#4"
