from policyengine_us.model_api import *


class pell_grant_head_allowances(Variable):
    value_type = float
    entity = Person
    label = "Head Allowances"
    definition_period = YEAR
