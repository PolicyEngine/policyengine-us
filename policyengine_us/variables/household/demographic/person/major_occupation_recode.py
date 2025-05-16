from policyengine_us.model_api import *


class major_occupation_recode(Variable):
    value_type = int
    entity = Person
    label = "CPS major occupation recode"
    documentation = "This variable is the A_MJOCC variable in the Current Population Survey."
    definition_period = YEAR
