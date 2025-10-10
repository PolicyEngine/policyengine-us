from policyengine_us.model_api import *


class vehicles_loan_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of loaned vehicles in SPM unit"
    definition_period = YEAR

    adds = ["has_vehicle_loan"]
