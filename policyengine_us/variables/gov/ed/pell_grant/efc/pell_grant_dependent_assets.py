from policyengine_us.model_api import *


class pell_grant_dependent_assets(Variable):
    value_type = float
    entity = Person
    label = "Dependent Assets"
    definition_period = YEAR
