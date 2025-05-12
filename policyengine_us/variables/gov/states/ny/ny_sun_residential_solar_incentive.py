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
        p = parameters(period).gov.states.ny
        ny_sun_new_pw_system_size = household("ny_sun_new_pw_system_size",period)
        region = household("ny_sun_region_status", period)
        incentive_percentage = p.amount[region]

        #same issue as with household size - ny_sun_current_solar_energy_use is a user input
        ny_sun_current_solar_energy_use = household("ny_sun_current_solar_energy_use",period)
        multiplier = p.max_pv_system_size
        max_kwh = ny_sun_current_solar_energy_use * multiplier
        #Conversion factor of 1 kW=1 kWh / 3600 (for number of seconds in an hr)
        max_kw = max_kwh / 3600  
        approved_kw = min(max_kw, ny_sun_new_pw_system_size)
        #incentive_rate = p.amount.calc(period)
        return approved_kw * 1000 * incentive_percentage

