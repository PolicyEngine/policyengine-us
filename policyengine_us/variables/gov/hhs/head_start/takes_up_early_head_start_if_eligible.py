from policyengine_us.model_api import *


class takes_up_early_head_start_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Takes up Early Head Start if eligible"
    definition_period = YEAR

    def formula(person, period, parameters):
        draw = person("early_head_start_takeup_draw", period)
        rate = parameters(
            period
        ).gov.hhs.head_start.early_head_start.takeup_rate
        return draw < rate
