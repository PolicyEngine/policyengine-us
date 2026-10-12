from policyengine_us.model_api import *


class receives_medicaid_long_term_care_services(Variable):
    value_type = bool
    entity = Person
    label = "Receives Medicaid long-term care services"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f"

    def formula(person, period, parameters):
        return person("is_in_medicaid_facility", period)
