from policyengine_us.model_api import *


class pell_grant_parent_income(Variable):
    value_type = float
    entity = Person
    label = "Parent Income"
    definition_period = YEAR
