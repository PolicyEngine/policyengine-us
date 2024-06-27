from policyengine_us.model_api import *

class nyserda_drive_clean_vehicle_electric_range(Variable):
    value_type = float
    entity = Household
    label = "All-Electric Vehicle Range"
    unit = miles
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf"
    defined_for = StateCode.NY