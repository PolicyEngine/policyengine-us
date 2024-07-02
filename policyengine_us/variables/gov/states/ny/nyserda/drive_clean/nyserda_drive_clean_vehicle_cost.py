from policyengine_us.model_api import *

class nyserda_drive_clean_vehicle_cost(Variable):
    value_type = float
    entity = Household
    label = "Vehicle Price"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8"
    defined_for = StateCode.NY