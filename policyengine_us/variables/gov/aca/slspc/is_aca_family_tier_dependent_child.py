from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.is_aca_ny_age_29_dependent_child import (
    ny_age_29_child_condition,
)


def family_tier_child_condition(person, period, parameters):
    """The family-tier dependent-child test without the premium condition."""
    p = parameters(period).gov.aca
    age = person("monthly_age", period)
    is_tax_dependent = person("is_tax_unit_dependent", period)
    under_child_only_age = age <= p.slcsp.max_child_age
    under_age_threshold = age < p.family_tier_dependent_child_age_threshold
    return (
        under_child_only_age
        | (is_tax_dependent & under_age_threshold)
        | ny_age_29_child_condition(person, period, parameters)
    )


class is_aca_family_tier_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Person is a dependent child for ACA family tier premiums"
    definition_period = MONTH

    def formula(person, period, parameters):
        return person("pays_aca_premium", period) & family_tier_child_condition(
            person, period, parameters
        )
