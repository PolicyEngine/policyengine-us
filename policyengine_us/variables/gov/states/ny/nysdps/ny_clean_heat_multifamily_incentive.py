from policyengine_us.model_api import *


class ny_clean_heat_multifamily_incentive(Variable):
    value_type = float
    entity = Household
    label = "New York Clean Heat incentive for multifamily (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump for multifamily"
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY

    def formula(household, period, parameters):
        """
        Calculates the incentive and the cap for the NYS Clean Heat program.

        Parameters:
        - parameters (instance)
        - period (int)
        - household (instance)

        Returns:
        - float: a capped incentive (float).
        """
        p = parameters(
            period
        ).gov.states.ny.nysdps.clean_heat.clean_heat_con_edison

        source = household("ny_clean_heat_source_category", period)
        heat_pump = household("ny_clean_heat_heat_pump_category", period)
        building = household("ny_clean_heat_building_category", period)

        # calc uncapped incentive
        uncapped_incentive = p.multifamily.amount[source][building][heat_pump]

        # multiply uncapped incentive by MMBtu/dwelling_unit
        mmbtu = household("ny_clean_heat_mmbtu", period)

        max_unit = p.multifamily.dwelling_unit_cap
        uncapped_dwelling_unit = household(
            "ny_clean_heat_dwelling_units", period
        )
        dwelling_unit = min_(max_unit, uncapped_dwelling_unit)

        uncapped_incentive = select(
            [
                # C2C, C6A
                (heat_pump == heat_pump.possible_values.C2C)
                | (heat_pump == heat_pump.possible_values.C6A),
                # C4, C4A, C6, C10
                (heat_pump == heat_pump.possible_values.C4)
                | (heat_pump == heat_pump.possible_values.C4A1)
                | (heat_pump == heat_pump.possible_values.C4A2)
                | (heat_pump == heat_pump.possible_values.C6)
                | (heat_pump == heat_pump.possible_values.C10),
            ],
            [
                # multiply by dwelling_unit
                uncapped_incentive * dwelling_unit,
                # multiply by mmbtu
                uncapped_incentive * mmbtu,
            ],
        )

        # calc cap amount
        project_cost = household("ny_clean_heat_project_cost", period)
        cap = project_cost * p.multifamily.rate

        # calc capped incentive
        return min(uncapped_incentive, cap, p.multifamily.cap)
