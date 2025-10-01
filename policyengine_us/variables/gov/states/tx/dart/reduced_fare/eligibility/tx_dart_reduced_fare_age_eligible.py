from policyengine_us.model_api import *


class tx_dart_reduced_fare_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Dallas Area Rapid Transit (DART) Reduced Fare program due to age"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dart.reduced_fare.age_threshold
        age = person("age", period)

        # Senior (65+)
        senior_eligible = age >= p.senior
        # Child (5-14)
        child_eligible = p.child.calc(age)

        return senior_eligible | child_eligible
