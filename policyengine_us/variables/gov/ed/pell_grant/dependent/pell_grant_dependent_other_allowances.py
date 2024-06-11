from policyengine_us.model_api import *


class pell_grant_dependent_other_allowances(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant dependent other allowances"
    definition_period = YEAR
