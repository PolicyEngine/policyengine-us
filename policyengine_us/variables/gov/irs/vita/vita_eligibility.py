from policyengine_us.model_api import *


class vita_eligibility(Variable):
    value_type = bool
    entity = Person
    label = "IRS Vita program eligibility"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.vita.eligibility
        income = person("irs_gross_income", period)
        is_eligible_income = income <= p.income_limit
        is_disabled = person("is_disabled", period)
        is_eligible_language = person("is_english_proficient", period)
        eligible = is_eligible_income | is_disabled | ~is_eligible_language

        return eligible
