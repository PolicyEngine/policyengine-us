from policyengine_us.model_api import *


class social_security_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits"
    unit = USD
    uprating = "gov.ssa.uprating"

    def formula(person, period, parameters):
        # Get benefit before earnings test
        benefit_before_test = person(
            "ss_retirement_benefit_before_earnings_test", period
        )

        # Apply earnings test reduction
        earnings_test_reduction = person("ss_earnings_test_reduction", period)
        benefit_after_test = max_(
            0, benefit_before_test - earnings_test_reduction
        )

        # TODO: Apply family maximum
        # TODO: Apply GPO/WEP if applicable

        return benefit_after_test
