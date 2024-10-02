from policyengine_us.model_api import *


class co_chp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Colorado Child Health Plan Plus eligibility"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        medicaid_eligible = person("is_medicaid_eligible", period)
        income_level = person("medicaid_income_level", period)
        p = parameters(period).gov.states.co.hcpf.chp
        in_income_range = income_level <= p.income_limit
        age = person("age", period)
        is_child = p.child.calc(age)
        is_pregnant = person("is_pregnant", period)
        is_age_eligible = is_pregnant | is_child
        return ~medicaid_eligible & is_age_eligible & in_income_range
