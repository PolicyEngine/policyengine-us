from policyengine_us.model_api import *


class never_eligible_for_social_security_benefits(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Never eligible for Social Security"

    def formula(person, period, parameters):
        # Preserve the existing heuristic for baseline data while still
        # allowing same-period reported overrides through set_input.
        age = person("age", period)
        social_security_holder = person.simulation.get_holder("social_security")
        social_security_known = period in social_security_holder.get_known_periods()
        social_security = person("social_security", period)
        return (age >= 70) & social_security_known & (social_security == 0)
