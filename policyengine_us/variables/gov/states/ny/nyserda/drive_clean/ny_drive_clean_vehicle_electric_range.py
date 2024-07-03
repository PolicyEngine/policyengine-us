from policyengine_us.model_api import *


class ny_drive_clean_vehicle_electric_range(Variable):
    value_type = float
    entity = Household
    label = "New York Drive Clean rebate program all-electric vehicle range"
    unit = "miles"
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8"
    defined_for = StateCode.NY
