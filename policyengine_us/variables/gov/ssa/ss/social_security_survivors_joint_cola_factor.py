from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    reported_joint_cola_factor,
)


class social_security_survivors_joint_cola_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Joint Social Security survivors COLA factor"
    documentation = (
        "One payment-event numerator combines adjusted COLAs and withholding."
    )

    def formula(person, period, parameters):
        return reported_joint_cola_factor(person, period, parameters, "survivors")
