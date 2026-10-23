from policyengine_us.model_api import *


class social_security_retirement_payable_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement payable factor"

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.ssa.benefit_levers.payable
        factor = person("social_security_payable_factor", period)
        return 1 if p.oasi_only and "retirement" == "disability" else factor
