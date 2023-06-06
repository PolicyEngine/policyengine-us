from policyengine_us.model_api import *


class co_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Colorado State Supplement Eligible"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        ssi_eligible = person("is_ssi_eligible_individual", period)
        is_disabled = person("is_ssi_disabled", period)
        is_blind = person("is_blind", period)
        disabled_or_blind = is_disabled | is_blind
        age = person("age", period)
        p = parameters(period).gov.states.co.ssa.state_supplement
        in_age_range = p.age_range.calc(age)
        return disabled_or_blind & ssi_eligible & in_age_range
