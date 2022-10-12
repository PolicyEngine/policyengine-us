from policyengine_us.model_api import *


class ca_cvrp_vehicle_rebate_amount(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "CVRP rebate for purchased vehicle"
    unit = USD
    documentation = "Rebate value for a purchased vehicle under the California Clean Vehicle Rebate Project (CVRP)"
    reference = "https://cleanvehiclerebate.org/en/eligible-vehicles"
    defined_for = StateCode.CA
