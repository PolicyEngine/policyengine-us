from policyengine_us.model_api import *


class basic_health_program_ny_age_29_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Basic Health Program New York Age 29 dependent child"
    definition_period = MONTH
    defined_for = "basic_health_program_enrolled"
    reference = "https://www.nysenate.gov/legislation/laws/ISC/3216"

    def formula(person, period, parameters):
        p = parameters(period).gov.aca
        state_code = person.household("state_code", period)
        age = person("monthly_age", period)
        return (
            (state_code == state_code.possible_values.NY)
            & (age >= p.family_tier_dependent_child_age_threshold)
            & (age < p.ny_age_29_dependent_child_age_threshold)
            & person("is_tax_unit_dependent", period)
        )
