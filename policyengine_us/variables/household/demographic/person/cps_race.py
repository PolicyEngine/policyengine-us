from policyengine_us.model_api import *


class cps_race(Variable):
    value_type = int
    entity = Person
    label = "CPS racial category"
    documentation = "This variable is the PRDTRACE variable in the Current Population Survey."
    definition_period = YEAR
