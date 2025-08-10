from policyengine_us.model_api import *


class is_aca_eshi_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for employer-sponsored health insurance "
        "under ACA rules"  # if this is true, person is ineligible for ACA PTC
    )
    definition_period = YEAR

    def formula(person, period, parameters):

        has = person("has_esi", period)  # has ESI
        offered = person(
            "offered_aca_disqualifying_esi", period
        )  # being offered disqualifying ESI
        return has | offered
