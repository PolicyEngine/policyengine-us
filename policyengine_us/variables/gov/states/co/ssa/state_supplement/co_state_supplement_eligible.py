from policyengine_us.model_api import *


class co_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Colorado State Supplement Eligible"
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        ssi_eligible = person("is_ssi_eligible_individual", period.this_year)
        is_disabled = person("is_ssi_disabled", period.this_year)
        is_blind = person("is_blind", period.this_year)
        disabled_or_blind = is_disabled | is_blind
        age = person("age", period.this_year)
        p = parameters(period).gov.states.co.ssa.state_supplement
        in_age_range = p.age_range.calc(age)
        return disabled_or_blind & ssi_eligible & in_age_range
