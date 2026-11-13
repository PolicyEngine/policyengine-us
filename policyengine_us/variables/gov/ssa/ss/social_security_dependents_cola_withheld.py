from policyengine_us.model_api import *
from policyengine_us.tools.social_security.means_test import component_withholding


class social_security_dependents_cola_withheld(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents COLA withheld under A5"
    documentation = "Legacy manual decision when the means test is disabled; E3 uses the separate tri-state COLA override."


class social_security_dependents_cola_override(Variable):
    value_type = int
    default_value = -1
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents COLA means-test override"
    documentation = "Exact payment-year E3 decision: -1 automatic (default), 0 paid, 1 withheld. Omitted people remain automatic."


class social_security_dependents_cola_means_test_withheld(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents resolved COLA means-test decision"
    documentation = "Automatic prior-year income decision with a separate per-person tri-state override; returns the legacy manual decision with E3 disabled."

    def formula(person, period, parameters):
        return component_withholding(person, period, parameters, "dependents")
