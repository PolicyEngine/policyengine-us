from policyengine_us.model_api import *


class pell_grant_dependent_available_income(Variable):
    value_type = float
    entity = Person
    label = "Dependent Availble Income"
    definition_period = YEAR
