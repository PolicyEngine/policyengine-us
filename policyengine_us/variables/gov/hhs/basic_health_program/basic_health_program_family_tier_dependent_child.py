from policyengine_us.model_api import *


class basic_health_program_family_tier_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Basic Health Program family tier dependent child"
    definition_period = MONTH
    defined_for = "basic_health_program_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.aca
        age = person("monthly_age", period)
        return (
            (age <= p.slcsp.max_child_age)
            | (
                person("is_tax_unit_dependent", period)
                & (age < p.family_tier_dependent_child_age_threshold)
            )
            | person("basic_health_program_ny_age_29_dependent_child", period)
        )
