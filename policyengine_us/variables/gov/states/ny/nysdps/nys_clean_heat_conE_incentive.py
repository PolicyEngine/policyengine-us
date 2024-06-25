from policyengine_us.model_api import *

class nys_clean_heat_conE_incentive(Variable):
    value_type = float  # TODO: need to change?
    entity = TaxUnit
    label = "New York State Clean Heat incentive (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump"
    
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf"
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

        p = parameters(period).gov.states.ny.nysdps.nys_clean_heat
        cost = tax_unit("nys_clean_heat_conE_project_cost", period)

        var0 = tax_unit("nys_clean_heat_conE_family_type", period)
        var1 = tax_unit("nys_clean_heat_conE_heat_pump", period)

        # Residential
        if var0.status == 'Residential':
            var2 = tax_unit("nys_clean_heat_conE_family_dac", period)    
            if var1.status == 'ASHP':
                var3 = tax_unit("nys_clean_heat_conE_home", period)
                var4 = tax_unit("nys_clean_heat_conE_heat_pump_type", period)
                uncapped_incentive = \
                    p.conE_incentive[var0.status][var1.status][var2.status][var3.status][var4.status]
            else:
                uncapped_incentive = p.conE_incentive[var0.status][var1.status][var2.status]

            # Calculate cap
            rate = p.conE_rate[var2]
            cap = cost * rate

            incentive = min(uncapped_incentive, cap)            
            return incentive

        # Multifamily
        else:
            var5 = tax_unit("nys_clean_heat_conE_building", period)
            var6 = tax_unit("nys_clean_heat_conE_description", period)
            uncapped_incentive = p.conE_incentive[var0.status][var1.status][var5.status][var6.status]

            # Calculate cap                             
            rate = p.conE_rate[var0]
            cap = cost * rate
            cap = min(cap, p.conE_cap_amount)

            if var6.status == "Multifamily Full Load ASHP Heating with Decommissioning":
                max_unit = p.conE_cap_unit
                return uncapped_incentive, cap, max_unit

            return uncapped_incentive, cap
