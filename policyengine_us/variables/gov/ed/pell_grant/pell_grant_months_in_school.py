from policyengine_us.model_api import *


class pell_grant_months_in_school(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant months of year student is in school"
    definition_period = YEAR
