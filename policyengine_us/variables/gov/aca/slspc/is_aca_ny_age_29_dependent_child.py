from policyengine_us.model_api import *


class is_aca_ny_age_29_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Person is a New York Age 29 dependent child for ACA family tier premiums"
    definition_period = MONTH

    def formula(person, period, parameters):
        p = parameters(period).gov.aca
        state_code = person.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY
        age = person("monthly_age", period)
        lower_age = p.family_tier_dependent_child_age_threshold
        upper_age = p.ny_age_29_dependent_child_age_threshold
        in_age_range = (age >= lower_age) & (age < upper_age)
        is_tax_dependent = person("is_tax_unit_dependent", period)
        return (
            person("pays_aca_premium", period) & in_ny & in_age_range & is_tax_dependent
        )
