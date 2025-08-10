from policyengine_us.model_api import *


class ss_retirement_benefit_before_earnings_test(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefit before earnings test"
    documentation = "Annual Social Security retirement benefit before applying earnings test"
    unit = USD
    defined_for = "ss_retirement_eligible"
    reference = (
        "https://www.ssa.gov/benefits/retirement/",
        "https://www.law.cornell.edu/uscode/text/42/402#a",
    )

    def formula(person, period, parameters):
        # Get PIA
        pia = person("ss_pia", period)

        # Get retirement age adjustment factor
        adjustment_factor = person(
            "ss_retirement_age_adjustment_factor", period
        )

        # Calculate monthly benefit
        monthly_benefit = pia * adjustment_factor

        # Convert to annual
        annual_benefit = monthly_benefit * MONTHS_IN_YEAR

        return annual_benefit
