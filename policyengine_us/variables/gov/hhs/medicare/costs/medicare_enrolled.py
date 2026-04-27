from policyengine_us.model_api import *


class medicare_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicare enrolled"
    documentation = "Whether the person is enrolled in Medicare (Part A and/or Part B)"
    definition_period = YEAR
    reference = "https://www.cms.gov/medicare"
    default_value = False
