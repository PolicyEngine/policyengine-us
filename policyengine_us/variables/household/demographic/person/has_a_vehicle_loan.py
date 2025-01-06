from policyengine_us.model_api import *


class has_vehicle_loan(Variable):
    value_type = bool
    entity = Person
    label = "Person took out a vehicle loan or lease"
    definition_period = YEAR
