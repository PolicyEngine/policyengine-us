from policyengine_us.model_api import *


class social_security_survivors_payable_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security survivors payable factor"

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.ssa.benefit_levers.payable
        factor = person("social_security_payable_factor", period)
        return 1 if p.oasi_only and "survivors" == "disability" else factor
