from policyengine_us.model_api import *


class pell_grant_head_assets(Variable):
    value_type = float
    entity = Person
    label = "Head Assets"
    definition_period = YEAR
