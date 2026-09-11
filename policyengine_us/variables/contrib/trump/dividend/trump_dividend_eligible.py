from policyengine_us.model_api import *


class trump_dividend_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Trump dividend eligible"
    documentation = "Eligible for the Trump dividend."
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.contrib.trump.dividend
        if not p.in_effect:
            return False
        age = person("age", period)
        meets_age_requirement = age >= p.min_age
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        eligible_immigration_status = np.isin(
            immigration_status_str, p.eligible_immigration_statuses
        )
        return meets_age_requirement & eligible_immigration_status
