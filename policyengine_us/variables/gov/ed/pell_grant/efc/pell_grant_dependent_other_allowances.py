from policyengine_us.model_api import *


class pell_grant_dependent_other_allowances(Variable):
    value_type = float
    entity = Person
    label = "Dependent Other Allowances"
    definition_period = YEAR
