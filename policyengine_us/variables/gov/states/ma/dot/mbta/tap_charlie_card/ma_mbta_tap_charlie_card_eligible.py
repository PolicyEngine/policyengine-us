from policyengine_us.model_api import *


class ma_mbta_tap_charlie_card_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Massachusetts Bay Transportation Authority Transportation Access Pass (TAP) Charlie Card program"
    reference = "https://www.mbta.com/fares/reduced/transportation-access-pass"
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        disabled = person("is_disabled", period)
        medicare_eligible = person("is_medicare_eligible", period)
        return disabled | medicare_eligible
