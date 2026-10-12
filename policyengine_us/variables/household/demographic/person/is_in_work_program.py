from policyengine_us.model_api import *


class is_in_work_program(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Is in a work program"
    documentation = "Whether the person is participating in a state, county, or federal work program tied to a benefit (for example, a welfare-to-work activity, SNAP Employment and Training, or a county work center)."
