from policyengine_us.model_api import *


class social_security_payable_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security supplied payable-share factor"
    documentation = "Externally supplied annual share, including a supplier-blended depletion year; no depletion projection is inferred."

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.ssa.benefit_levers.payable
        if not np.isfinite(p.share) or not 0 <= p.share <= 1:
            raise ValueError("Social Security payable share must lie in [0, 1]")
        return p.share
