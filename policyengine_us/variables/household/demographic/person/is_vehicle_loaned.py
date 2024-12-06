from policyengine_us.model_api import *


class is_vehicle_loaned(Variable):
    value_type = bool
    entity = Person
    label = "Is the vehicel loaned or leased"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("vehicle_mortgage_expense",period) > 0
