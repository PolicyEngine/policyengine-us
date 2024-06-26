from policyengine_us.model_api import *

class ny_clean_heat_incentive(Variable):
    value_type = float  # TODO: need to change?
    entity = TaxUnit
    label = "New York State Clean Heat incentive (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump"
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY

    def formula(parameters, period, tax_unit):
        '''
        Calculates the incentive and the cap for the NYS Clean Heat program.

        Parameters:
        - parameters (instance)
        - period (int)
        - tax_unit (instance)

        Returns:
        - float or tuple: For residential, a capped incentive (float). 
          For multifamily, a tuple with the uncapped incentive (float), the cap (float), and maximum dwelling unit (int) if necessary.
        '''

        p = parameters(period).gov.states.ny.nysdps.con_edison_clean_heat
        project_cost = tax_unit("ny_clean_heat_project_cost", period)

        family_type = tax_unit("ny_clean_heat_family_type_category", period) #var0
        heat_pump = tax_unit("ny_clean_heat_heat_pump_category", period) #var1

        # Residential
        if family_type.status == 'Residential':
            dac = tax_unit("ny_clean_heat_dac_category", period) #var2
            if heat_pump.status == 'ASHP':
                home = tax_unit("ny_clean_heat_home_category", period) #var3
                heat_pump_type = tax_unit("ny_clean_heat_heat_pump_type_category", period) #var4
                uncapped_incentive = \
                    p.amount[family_type][heat_pump][dac][home][heat_pump_type]
            else:
                uncapped_incentive = p.amount[family_type][heat_pump][dac]

            # Calculate cap
            rate = p.rate[dac]
            cap = project_cost * rate

            incentive = min(uncapped_incentive, cap)
            return incentive

        # Multifamily
        else:
            building = tax_unit("ny_clean_heat_building_category", period) #var5
            description = tax_unit("ny_clean_heat_description_category", period) #var6
            uncapped_incentive = p.conE_incentive[family_type][heat_pump][building][description]

            # Calculate cap
            rate = p.rate[family_type]
            cap = project_cost * rate
            cap = min(cap, p.cap)

            if description.status == "Multifamily Full Load ASHP Heating with Decommissioning":
                max_unit = p.dwelling_unit_cap
                return uncapped_incentive, cap, max_unit

            return uncapped_incentive, cap
