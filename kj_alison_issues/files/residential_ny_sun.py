from ... policyengine_us.model_api import *
from ... policyengine_us.entities import *
from ... policyengine_us.tools.general import *
from ... policyengine_us.tools.documentation import Enum 

class residential_solar_ny_sun(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Incentive given"
    documentation = "Eligible for nonrefundable credit for the purchase of a new clean vehicle" #to change 
    unit = USD
    reference = "https://portal.nyserda.ny.gov/servlet/servlet.FileDownload?file=00P8z000001BIuBEAW" 
    defined_for = StateCode.NY 


    def formula(household, period, parameters):
        # region = household("region_incentive", period)
        p = parameters(period).parameters.gov.states.ny
        home_solar_size = household("home_solar_size",period)
        prev_size = household("prev_size",period)
        max_multiplier = p.max_pv_system_size.calc(period)  
        max_kwh = prev_size * max_multiplier
        #Conversion factor of 1 kW=1 kWh / 3600 (for number of seconds in an hr)
        max_kw = max_kwh / 3600  
        approved_kw = min(max_kw, home_solar_size)
        incentive_rate = p.region_incentive.calc(period)
        return approved_kw * 1000 * incentive_rate


#home_solar_size, prev_size




