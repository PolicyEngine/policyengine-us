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

        family_type = tax_unit("ny_clean_heat_family_type_category", period) #var0
        heat_pump = tax_unit("ny_clean_heat_heat_pump_category", period) #var1
        dac = tax_unit("ny_clean_heat_dac_category", period) #var2
        home = tax_unit("ny_clean_heat_home_category", period) #var3
        heat_pump_type = tax_unit("ny_clean_heat_heat_pump_type_category", period) #var4
        building = tax_unit("ny_clean_heat_building_category", period) #var5
        description = tax_unit("ny_clean_heat_description_category", period) #var6

        # calc uncapped incentive
        uncapped_incentive =  select(
            [
                # residential -> ashp
                family_type == family_type.possible_values.RESIDENTIAL and heat_pump == heat_pump.possible_values.ASHP,
                # residential -> gshp
                family_type == family_type.possible_values.RESIDENTIAL and heat_pump == heat_pump.possible_values.GSHP,
                # multifamily
                family_type == family_type.possible_values.MULTIFAMILY,
            ],
            [
                p.residential_ashp_amount[dac][home][heat_pump_type],
                p.residential_gshp_amount[dac],
                p.multifamily_amount[heat_pump][building][description],
            ],
        )

        # multipy uncapped incentive by MMBtu/dwelling_unit (if necessary)
        mmbtu = tax_unit('ny_clean_heat_mmbtu', period)

        max_unit = p.dwelling_unit_cap
        uncapped_dwelling_unit = tax_unit("ny_clean_heat_dwelling_unit", period)
        dwelling_unit = min(max_unit, uncapped_dwelling_unit)

        uncapped_incentive = select(
            [
                # residential
                family_type == family_type.possible_values.RESIDENTIAL,
                # multifamily -> C2 or C6A
                description == description.possible_values.C2 or description == description.possible_values.C6A,
                # multifamily -> C4, C4A, C6, C10
                family_type == family_type.possible_values.MULTIFAMILY and (
                    description == description.possible_values.C4 or \
                    description == description.possible_values.C4A1 or \
                    description == description.possible_values.C4A2 or \
                    description == description.possible_values.C6 or \
                    description == description.possible_values.C10),
            ],
            [
                # N/A
                uncapped_incentive,
                # multipy by dwelling_unit
                uncapped_incentive * dwelling_unit,
                # multipy by mmbtu
                uncapped_incentive * mmbtu,
            ],
        )

        # calc cap amount
        rate = select(
            [
                family_type == family_type.possible_values.RESIDENTIAL,
                family_type == family_type.possible_values.MULTIFAMILY,
            ],
            [
                p.residential_rate[dac],
                p.multifamily_rate,

            ],
        )
        project_cost = tax_unit("ny_clean_heat_project_cost", period)
        cap = project_cost * rate

        # calc capped incentive
        family_type_bool = family_type == family_type.possible_values.RESIDENTIAL
        incentive = where(family_type_bool, min(uncapped_incentive, cap), min(uncapped_incentive, cap, p.cap))

        return incentive
