from policyengine_us.model_api import *


class vita_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the VITA program"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.vita.eligibility
        income = person("irs_gross_income", period)
        is_eligible_income = income <= p.income_limit
        is_disabled = person("is_disabled", period)
        proficient_in_english = person("is_english_proficient", period)
        return is_eligible_income | is_disabled | ~proficient_in_english
