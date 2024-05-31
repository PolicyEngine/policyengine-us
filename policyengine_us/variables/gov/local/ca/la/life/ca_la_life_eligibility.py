from policyengine_us.model_api import *


class ca_la_life_eligibility(Variable):
    value_type = bool
    entity = Person
    label = "LA metro LIFE program eligibility"
    definition_period = YEAR
    defined_for = "in_la"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.la.life

        household_size = person.household("household_size", period)
        household_income = person.household("household_net_income", period)
        income_eligible = household_income <= p.eligibility.calc(
            household_size
        )

        is_child = person("is_child", period)
        if is_child:
            age_eligible = person("is_child_of_tax_head", period) & (
                household_size >= 2
            )
        else:
            age_eligible = True

        snap_eligible = person.spm_unit("is_snap_eligible", period)
        social_security_eligible = person("social_security", period) > 0
        social_security_disability_eligible = (
            person("social_security_disability", period) > 0
        )
        tanf_eligible = person.spm_unit("is_tanf_eligible", period)

        return age_eligible & (
            income_eligible
            | snap_eligible
            | social_security_eligible
            | social_security_disability_eligible
            | tanf_eligible
        )
