from policyengine_us.model_api import *


class pell_grant_head_allowances(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant head allowances"
    definition_period = YEAR
