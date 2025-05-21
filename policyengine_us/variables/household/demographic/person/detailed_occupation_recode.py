from policyengine_us.model_api import *


class detailed_occupation_recode(Variable):
    value_type = int
    entity = Person
    label = "CPS detailed occupation recode of previous year"
    documentation = "This variable is the POCCU2 variable in the Current Population Survey."
    definition_period = YEAR
