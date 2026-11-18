from policyengine_us.model_api import *


class co_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Colorado State Supplement Eligible"
    definition_period = MONTH
    defined_for = StateCode.CO
    # PDF pages 91-92
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=91"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.546 and 3.547(A), (D): AND-CS is for clients
        # "receiving SSI due to a disability or blindness". 3.548(A)
        # calculates grants "on an individual basis with just one client per
        # case", so each member of an SSI couple qualifies on their own.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        is_disabled = person("is_ssi_disabled", period.this_year)
        is_blind = person("is_blind", period.this_year)
        disabled_or_blind = is_disabled | is_blind
        age = person("age", period.this_year)
        p = parameters(period).gov.states.co.ssa.state_supplement
        in_age_range = p.age_range.calc(age)
        return disabled_or_blind & receives_ssi & in_age_range
