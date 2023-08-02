from policyengine_us.model_api import *


class pell_grant_months_in_school(Variable):
    value_type = float
    entity = Person
    label = "Percent of Year Student is in School"
    definition_period = YEAR
    default_value = 9
