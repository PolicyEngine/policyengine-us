from policyengine_us.model_api import *


class ca_la_life_eligibility(Variable):
    value_type = bool
    entity = Person
    label = "LA metro LIFE eligibility"
    definition_period = YEAR
    defined_for = "in_la"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.la.life

        household_size = person.household("household_size", period)
        household_income = person.household("household_net_income", period)
        income_eligible = household_income <= p.income_threshold.calc(
            household_size
        )

        is_child = person("is_child", period)
        age_eligible = where(
            is_child,
            person("is_child_of_tax_head", period),
            True,
        )

        ca_la_life_program_eligible = (
            person("ca_la_life_program_eligible", period) > 0
        )

        return age_eligible & (income_eligible | ca_la_life_program_eligible)
