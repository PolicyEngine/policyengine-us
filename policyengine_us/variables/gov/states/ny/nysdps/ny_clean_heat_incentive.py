from policyengine_us.model_api import *

class ny_clean_heat_incentive(Variable):
    value_type = float
    entity = Household
    label = "New York Clean Heat incentive (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump"
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY

    def formula(household, period, parameters):
        '''
        Calculates the incentive and the cap for the NYS Clean Heat program.

        Parameters:
        - parameters (instance)
        - period (int)
        - household (instance)

        Returns:
        - float: a capped incentive (float). 
        '''
    
        p = parameters(period).gov.states.ny.nysdps.clean_heat.clean_heat_con_edison

        family_type = household("ny_clean_heat_family_type_category", period) 
        source = household("ny_clean_heat_source_category", period)
        dac = household("ny_clean_heat_dac_category", period)
        home = household("ny_clean_heat_home_category", period)
        heat_pump = household("ny_clean_heat_heat_pump_category", period)
        building = household("ny_clean_heat_building_category", period)

        # calc uncapped incentive
        uncapped_incentive =  select(
            [
                # residential -> ashp
                family_type == family_type.possible_values.RESIDENTIAL and source == source.possible_values.ASHP,
                # residential -> gshp
                family_type == family_type.possible_values.RESIDENTIAL and source == source.possible_values.GSHP,
                # multifamily
                family_type == family_type.possible_values.MULTIFAMILY,
            ],
            [
                p.amount.ashp[dac][home][heat_pump],
                p.amount.gshp[dac],
                p.multifamily.amount[source][building][heat_pump],
            ],
        )

        # multipy uncapped incentive by MMBtu/dwelling_unit (if necessary)
        mmbtu = household('ny_clean_heat_mmbtu', period)

        max_unit = p.multifamily.dwelling_unit_cap
        uncapped_dwelling_unit = household("ny_clean_heat_dwelling_units", period)
        dwelling_unit = min_(max_unit, uncapped_dwelling_unit)

        uncapped_incentive = select(
            [
                # residential
                family_type == family_type.possible_values.RESIDENTIAL,
                # multifamily -> C2C or C6A
                heat_pump == heat_pump.possible_values.C2C or heat_pump == heat_pump.possible_values.C6A,
                # multifamily -> C4, C4A, C6, C10
                family_type == family_type.possible_values.MULTIFAMILY and (
                    heat_pump == heat_pump.possible_values.C4 or \
                    heat_pump == heat_pump.possible_values.C4A1 or \
                    heat_pump == heat_pump.possible_values.C4A2 or \
                    heat_pump == heat_pump.possible_values.C6 or \
                    heat_pump == heat_pump.possible_values.C10),
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
                p.residential.rate[dac],
                p.multifamily.rate,

            ],
        )
        project_cost = household("ny_clean_heat_project_cost", period)
        cap = project_cost * rate

        # calc capped incentive
        family_type_bool = family_type == family_type.possible_values.RESIDENTIAL
        min_incentive_residential = min_(uncapped_incentive, cap)
        min_incentive_multifamily = min(uncapped_incentive, cap, p.multifamily.cap)

        return where(family_type_bool, min_incentive_residential, min_incentive_multifamily)
