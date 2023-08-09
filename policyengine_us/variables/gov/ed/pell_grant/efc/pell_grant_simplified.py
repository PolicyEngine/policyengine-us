from policyengine_us.model_api import *


class pell_grant_simplified(Variable):
    value_type = bool
    entity = Person
    label = "Use Pell Grant simplified formula"
    definition_period = YEAR
