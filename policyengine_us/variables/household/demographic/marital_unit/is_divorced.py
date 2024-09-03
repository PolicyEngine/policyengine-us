from policyengine_us.model_api import *


class is_divorced(Variable):
    value_type = bool
    entity = Person
    label = "Divorced"
    documentation = "Whether the person is divorced from a partner."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/7703"
