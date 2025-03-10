from policyengine_us.model_api import *


class ma_mbta_senior_charlie_card_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Massachusetts Bay Transportation Authority Senior Charlie Card program"
    reference = "https://www.mbta.com/fares/reduced/senior-charliecard"
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.ma.dot.mbta.senior_charlie_card
        return age >= p.age_threshold
