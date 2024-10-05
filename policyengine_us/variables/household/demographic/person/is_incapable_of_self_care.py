from policyengine_us.model_api import *


class is_incapable_of_self_care(Variable):
    value_type = bool
    entity = Person
    label = "Incapable of self-care"
    documentation = "Whether this person is physically or mentally incapable of caring for themselves."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"
