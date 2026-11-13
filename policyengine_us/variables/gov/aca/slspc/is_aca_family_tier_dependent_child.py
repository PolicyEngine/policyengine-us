from policyengine_us.model_api import *


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
        | person("is_aca_ny_age_29_dependent_child", period)
    )


def family_tier_child_condition_for_enrollee(person, period, parameters):
    """Preserve supplied child classifications when repricing enrollees.

    The public predicate includes premium payment. A supplied predicate
    takes precedence for every enrollee in that month, including nonpayers.
    Otherwise use the calculated predicate for payers and the uncapped child
    condition for enrolled children who add no age-rated premium to the policy.
    """
    name = "is_aca_family_tier_dependent_child"
    if has_input_for_period(person.simulation, name, period):
        return person(name, period)
    return where(
        person("pays_aca_premium", period.this_year),
        person(name, period),
        family_tier_child_condition(person, period, parameters),
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
