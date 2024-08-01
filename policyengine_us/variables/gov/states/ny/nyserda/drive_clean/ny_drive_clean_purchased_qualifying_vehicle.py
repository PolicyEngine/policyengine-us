from policyengine_us.model_api import *


class ny_drive_clean_purchased_qualifying_vehicle(Variable):
    value_type = bool
    entity = Household
    label = "Purchased a qualifying new vehicle at an authorized dealership for the New York Drive Clean rebate program"
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#pages=6,7"
    defined_for = StateCode.NY
