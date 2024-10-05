from policyengine_us.model_api import *


class person_weight(Variable):
    value_type = float
    entity = Person
    label = "Person weight"
    definition_period = YEAR
    uprating = "calibration.gov.census.populations.total"

    def formula(person, period, parameters):
        return person.household("household_weight", period)
