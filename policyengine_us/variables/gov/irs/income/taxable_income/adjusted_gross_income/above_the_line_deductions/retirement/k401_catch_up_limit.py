from policyengine_us.model_api import *


class k401_catch_up_limit(Variable):
    value_type = float
    entity = Person
    label = "401(k) catch-up contribution limit"
    unit = USD
    documentation = (
        "Maximum additional 401(k) catch-up contribution for individuals "
        "age 50 or older. SECURE 2.0 enhanced limit applies for ages 60-63."
    )
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/cfr/text/26/1.414(v)-1",
        "https://www.law.cornell.edu/uscode/text/26/414#v_2_E",
    ]

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.irs.gross_income.retirement_contributions

        # Standard catch-up eligibility (age 50+)
        catch_up_eligible = age >= p.catch_up.age_threshold

        # Enhanced catch-up eligibility (ages 60-63, starting 2025)
        enhanced_min = p.catch_up.enhanced_age_min
        enhanced_max = p.catch_up.enhanced_age_max
        enhanced_eligible = (age >= enhanced_min) & (age <= enhanced_max)

        # Get applicable limits
        standard_limit = p.catch_up.limit.k401
        enhanced_limit = p.catch_up.limit.k401_enhanced

        # Apply enhanced limit for ages 60-63, standard for others 50+
        return where(
            enhanced_eligible,
            enhanced_limit,
            where(catch_up_eligible, standard_limit, 0),
        )
