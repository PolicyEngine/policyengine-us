from policyengine_us.model_api import *


class ma_mbta_income_eligible_reduced_fare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Massachusetts Bay Transportation Authority income-eligible reduced fare program"
    definition_period = YEAR
    defined_for = "ma_mbta_enrolled_in_applicable_programs"
    reference = "https://www.mbta.com/fares/reduced/income-eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dot.mbta.income_eligible_reduced_fares.age_threshold
        age = person("age", period)
        return p.calc(age)
