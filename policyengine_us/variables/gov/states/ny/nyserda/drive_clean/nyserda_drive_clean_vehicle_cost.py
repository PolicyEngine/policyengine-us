from policyengine_us.model_api import *

class nyserda_drive_clean_vehicle_cost(Variable):
    value_type = float
    entity = TaxUnit # TODO: Check if this is right. Not a tax credit.
    label = "Vehicle Price"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/All-Programs/Drive-Clean-Rebate-For-Electric-Cars-Program"
    defined_for = StateCode.NY