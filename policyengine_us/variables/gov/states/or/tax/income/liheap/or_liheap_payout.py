from policyengine_us.model_api import *

class liheap_region(Variable):
    value_type = str
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = "LIHEAP Region"
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55" 

    def formula(SPMUnit, period, parameters):
        county = SPMUnit("county_str", period)

        region1_counties = parameters(period).gov.states["or"].liheap.region1_counties

        region = select(
            [county in region1_counties],  
            ["Region 1"],                 
            default="Region 2"            
        )

        return region

class liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = "LIHEAP Payout"

    def formula(SPMUnit, period, parameters):
        payout = SPMUnit("utility_type", period)
        