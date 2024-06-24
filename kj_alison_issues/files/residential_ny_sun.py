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
    reference = "https://www.law.cornell.edu/uscode/text/26/30D" #to change 
    defined_for = "purchased_qualifying_new_clean_vehicle" #to change 


    def formula(tax_unit, home_solar_size, prev_size, period, parameters):
        region = tax_unit.household("region_incentive", period)
        p = parameters(period).
        #max_multiplier = parameters.get('max_pv_system_size_multiplier', 1.1)  
        max_kwh = tax_unit.household(prev_size) * max_multiplier
        max_kw = max_kwh / 1200  # Placeholder value
        max_watt = max_kw * 1000
        approved_kw = min(max_kw, home_solar_size)
        incentive_rate = region_incentive[region][str(period)]
        return approved_kw * incentive_rate







