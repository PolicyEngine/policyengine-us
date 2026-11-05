from policyengine_us.model_api import *


class social_security_across_the_board_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security across-the-board factor"

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.ssa.benefit_levers.across_the_board
        if not np.isfinite(p.rate) or p.rate < -1:
            raise ValueError(
                "Social Security across-the-board rate must be finite and at least -1"
            )
        return 1 + p.rate if period.start.year >= p.start_year else 1
