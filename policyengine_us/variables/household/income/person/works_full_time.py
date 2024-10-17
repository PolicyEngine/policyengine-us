from policyengine_us.model_api import *


class works_full_time(Variable):
    entity = Person
    label = "Whether the person worked full or part time"
    value_type = bool
    definition_period = YEAR

    # Not defining full or part time work based on weekly hours due to
    # the situation where a person works over 20 but is on a part-time contract
