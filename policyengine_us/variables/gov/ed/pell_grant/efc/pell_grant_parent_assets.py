from policyengine_us.model_api import *


class pell_grant_parent_assets(Variable):
    value_type = float
    entity = Person
    label = "Parent Assets"
    definition_period = YEAR
