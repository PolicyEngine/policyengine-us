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
        p = parameters(
            period
        ).gov.irs.gross_income.retirement_contributions.catch_up

        # Standard catch-up eligibility (age 50+)
        catch_up_eligible = age >= p.age_threshold

        # Enhanced catch-up eligibility (ages 60-63, starting 2025)
        enhanced_eligible = (age >= p.enhanced_age_min) & (
            age <= p.enhanced_age_max
        )

        # Apply enhanced limit for ages 60-63, standard for others 50+
        return where(
            enhanced_eligible,
            p.limit.k401_enhanced,
            where(catch_up_eligible, p.limit.k401, 0),
        )
