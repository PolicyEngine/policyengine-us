from policyengine_us.model_api import *

class ny_clean_heat_incentive(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York State Clean Heat incentive (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump"
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        '''
        Calculates the incentive and the cap for the NYS Clean Heat program.

        Parameters:
        - parameters (instance)
        - period (int)
        - tax_unit (instance)

        Returns:
        - float: a capped incentive (float). 
        '''
        
        p = parameters(period).gov.states.ny.nysdps.con_edison_clean_heat
        project_cost = tax_unit("ny_clean_heat_project_cost", period)

        family_type = tax_unit("ny_clean_heat_family_type_category", period) #var0
        heat_pump = tax_unit("ny_clean_heat_heat_pump_category", period) #var1

        # Residential
        if family_type == 'RESIDENTIAL':
            dac = tax_unit("ny_clean_heat_dac_category", period) #var2
            if heat_pump == 'ASHP':
                home = tax_unit("ny_clean_heat_home_category", period) #var3
                heat_pump_type = tax_unit("ny_clean_heat_heat_pump_type_category", period) #var4
                uncapped_incentive = \
                    p.residential_amount[heat_pump][dac][home][heat_pump_type]
            else:
                uncapped_incentive = p.residential_amount[heat_pump][dac]

            # Calculate cap
            rate = p.rate[family_type][dac]
            cap = project_cost * rate

            incentive = min(uncapped_incentive, cap)

        # Multifamily
        else:
            building = tax_unit("ny_clean_heat_building_category", period) #var5
            description = tax_unit("ny_clean_heat_description_category", period) #var6

            uncapped_incentive_unit = p.multifamily_amount[heat_pump][building][description]

            # per dwelling unit
            if description == "C2" or description == "C6A":
                max_unit = p.dwelling_unit_cap
                dwelling_unit = tax_unit("ny_clean_heat_dwelling_unit", period)
                unit = min(max_unit, dwelling_unit)
                uncapped_incentive = uncapped_incentive_unit * unit
            
            # per MMBtu
            else:
                mmbtu = tax_unit('ny_clean_heat_mmbtu', period)
                uncapped_incentive = uncapped_incentive_unit * mmbtu
            
            # Calculate cap
            rate = p.rate[family_type]
            cap = project_cost * rate

            incentive = min(cap, p.cap, uncapped_incentive)

        return incentive