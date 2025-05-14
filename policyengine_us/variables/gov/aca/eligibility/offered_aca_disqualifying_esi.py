from policyengine_us.model_api import *


class offered_aca_disqualifying_esi(Variable):
    value_type = bool
    entity = Person
    label = "Person is offered ACA disqualifying esi"
    definition_period = YEAR
