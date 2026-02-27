from policyengine_us.model_api import *


class social_security_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits"
    unit = USD
    uprating = "gov.ssa.uprating"

    def formula(person, period, parameters):
        p = parameters(period).gov.simulation
        use_reported = p.reported_social_security_retirement

        reported = person("social_security_retirement_reported", period)

        # Compute benefit from formula chain
        benefit_before_test = person(
            "ss_retirement_benefit_before_earnings_test", period
        )
        earnings_test_reduction = person("ss_earnings_test_reduction", period)
        computed = max_(0, benefit_before_test - earnings_test_reduction)

        return where(use_reported, reported, computed)
