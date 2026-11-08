from policyengine_us.model_api import *


class has_service_connected_disability(Variable):
    value_type = bool
    entity = Person
    label = "Is a veteran with a service-connected disability"
    documentation = (
        "Whether the person is a veteran with a disability incurred or "
        "aggravated in the line of duty in the active military, naval, air, "
        "or space service (38 U.S.C. 101(16)), at any disability rating. "
        "Defaults to is_fully_disabled_service_connected_veteran, since a "
        "fully disabled service-connected veteran has such a disability; set "
        "it to true for a veteran with a partial rating."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/38/101#16"

    def formula(person, period, parameters):
        return person("is_fully_disabled_service_connected_veteran", period)
