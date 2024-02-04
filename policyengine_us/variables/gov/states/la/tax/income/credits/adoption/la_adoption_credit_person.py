from policyengine_us.model_api import *


class la_adoption_credit_person(Variable):
    value_type = float
    entity = Person
    label = "Louisiana adoption credit for each person"
    reference = "https://legis.la.gov/legis/Law.aspx?d=1336834"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits.adoption
        child_age_eligible = person("age", period) <= p.age_threshold
        adopted_this_year = person("adopted_this_year", period)
        age_eligible_adopted_child = child_age_eligible & adopted_this_year
        return p.amount * age_eligible_adopted_child
