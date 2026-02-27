from policyengine_us.model_api import *


class social_security_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits"
    unit = USD
    uprating = "gov.ssa.uprating"

    def formula(person, period, parameters):
        # `reported_social_security_retirement` is a scalar simulation
        # parameter. Dispatch in Python so the unused branch is never
        # computed — the formula chain reaches back 45 years for AIME,
        # which would fail on historical periods without earnings data.
        if parameters(period).gov.simulation.reported_social_security_retirement:
            return person("social_security_retirement_reported", period)

        benefit_before_test = person(
            "ss_retirement_benefit_before_earnings_test", period
        )
        earnings_test_reduction = person("ss_earnings_test_reduction", period)
        return max_(0, benefit_before_test - earnings_test_reduction)
