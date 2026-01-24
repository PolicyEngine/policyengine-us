from policyengine_us.model_api import *


class weeks_unemployed(Variable):
    value_type = float
    entity = Person
    label = "weeks unemployed"
    unit = "week"
    documentation = (
        "Number of weeks during the year the person was looking for work. "
        "From CPS ASEC variable LKWEEKS."
    )
    definition_period = YEAR
