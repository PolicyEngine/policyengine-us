from policyengine_us.model_api import *


class pell_grant_dependents_in_college(Variable):
    value_type = int
    entity = Person
    label = "Dependents in College"
    definition_period = YEAR
