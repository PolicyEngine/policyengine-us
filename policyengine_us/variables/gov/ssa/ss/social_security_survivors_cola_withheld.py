from policyengine_us.model_api import *
from policyengine_us.tools.social_security.means_test import component_withholding


class social_security_survivors_cola_withheld(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors cola withheld"
    documentation = "Automatic prior-year income decision when the COLA means test is enabled, with explicit per-year decision overrides."

    def formula(person, period, parameters):
        return component_withholding(person, period, parameters, "survivors")
