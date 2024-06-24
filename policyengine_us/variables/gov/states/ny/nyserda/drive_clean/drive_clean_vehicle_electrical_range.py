from policyengine_us.model_api import *

class drive_clean_vehicle_electric_range(Variable):
    value_type = float
    entity = TaxUnit # TODO: Check if this is right. Not a tax credit.
    label = "All-Electric Vehicle Range"
    unit = miles
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/All-Programs/Drive-Clean-Rebate-For-Electric-Cars-Program"
    defined_for = StateCode.NY