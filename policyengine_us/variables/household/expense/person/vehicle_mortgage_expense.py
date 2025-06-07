from policyengine_us.model_api import *


class vehicle_mortgage_expense(Variable):
    value_type = float
    entity = Person
    label = "Vehicle mortgage expense"
    unit = USD
    definition_period = YEAR
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=4"
