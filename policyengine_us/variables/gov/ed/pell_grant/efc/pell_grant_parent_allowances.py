from policyengine_us.model_api import *


class pell_grant_parent_allowances(Variable):
    value_type = float
    entity = Person
    label = "Parent Allowances"
    definition_period = YEAR

    def formula(person, period, parameters):
        return 7_040
