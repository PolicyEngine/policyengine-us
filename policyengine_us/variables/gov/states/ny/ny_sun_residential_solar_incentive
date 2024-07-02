from policyengine_us.model_api import *


class ny_sun_residential_solar_incentive(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "New York SUN Incentive program"
    documentation = "Incentives for residential solar panels in NY"
    unit = USD
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW" 
    defined_for = StateCode.NY 


    def formula(household, period, parameters):
        #region = household("region_incentive", period)
        p = parameters(period).parameters.gov.states.ny
        #what should home_solar_size be? this is a user input
        home_solar_size = household("home_solar_size",period)
        region = household("ny_sun_region_status", period)
        incentive_percentage = p.amount[region]

        #same issue as with household size - prev size is a user input
        prev_size = household("household_size",period)
        multiplier = p.max_pv_system_size
        max_kwh = prev_size * multiplier
        #Conversion factor of 1 kW=1 kWh / 3600 (for number of seconds in an hr)
        max_kw = max_kwh / 3600  
        approved_kw = min(max_kw, home_solar_size)
        incentive_rate = p.amount.calc(period)
        return approved_kw * 1000 * incentive_rate

