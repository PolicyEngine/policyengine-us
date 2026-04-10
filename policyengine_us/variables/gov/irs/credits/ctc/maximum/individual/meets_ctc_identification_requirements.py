from policyengine_us.model_api import *


class meets_ctc_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person meets CTC identification requirements"
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        return person("has_valid_ssn", period)
