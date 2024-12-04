from policyengine_us.model_api import *


class ny_drive_clean_vehicle_cost(Variable):
    value_type = float
    entity = Household
    label = "Price of a qualifying vehicle purchased at an authorized New York dealership considered under the New York Drive Clean rebate program"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8"
    defined_for = "ny_drive_clean_purchased_qualifying_vehicle"
