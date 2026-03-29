from policyengine_us.model_api import *


class never_eligible_for_social_security_benefits(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Never eligible for Social Security"

    def formula(person, period, parameters):
        # Only apply this baseline heuristic when the underlying Social
        # Security component inputs are actually present for the period.
        # Sparse ad hoc sims should set this variable explicitly instead.
        age = person("age", period)
        social_security_known = any(
            period in person.simulation.get_holder(variable).get_known_periods()
            for variable in (
                "social_security_dependents",
                "social_security_disability",
                "social_security_retirement",
                "social_security_survivors",
            )
        )
        social_security = person("social_security", period)
        return (age >= 70) & social_security_known & (social_security == 0)
