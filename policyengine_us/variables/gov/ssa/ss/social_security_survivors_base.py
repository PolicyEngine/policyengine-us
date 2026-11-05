from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    selected_reported_benefit,
)


class social_security_survivors_base(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Selected Social Security survivors benefit base"

    def formula(person, period, parameters):
        return selected_reported_benefit(person, period, "survivors")
