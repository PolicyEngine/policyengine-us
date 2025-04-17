from policyengine_us.model_api import *


class ny_clean_heat_residential_incentive(Variable):
    value_type = float
    entity = Household
    label = "New York Clean Heat incentive for residential (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump for residential"
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
    defined_for = StateCode.NY

    def formula(household, period, parameters):
        """
        Calculates the incentive for the NYS Clean Heat program.

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
        dac = household("ny_clean_heat_dac_category", period)
        home = household("ny_clean_heat_home_category", period)
        heat_pump = household("ny_clean_heat_heat_pump_category", period)

        # calc uncapped incentive
        uncapped_incentive = select(
            [
                # ashp
                source == source.possible_values.ASHP,
                # gshp
                source == source.possible_values.GSHP,
            ],
            [
                p.amount.ashp[dac][home][heat_pump],
                p.amount.gshp[dac],
            ],
        )

        # calc cap amount
        project_cost = household("ny_clean_heat_project_cost", period)
        cap = project_cost * p.residential.rate[dac]

        # calc capped incentive
        return min_(uncapped_incentive, cap)
