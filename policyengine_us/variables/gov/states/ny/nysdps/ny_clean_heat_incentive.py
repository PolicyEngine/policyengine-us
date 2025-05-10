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

    def formula(household, period):
        """
        Calculates the incentive for the NYS Clean Heat program.

        Parameters:
        - period (int)
        - household (instance)

        Returns:
        - float: a capped incentive (float).
        """
        family_type = household("ny_clean_heat_family_type_category", period)

        family_type_bool = (
            family_type == family_type.possible_values.RESIDENTIAL
        )

        return where(
            family_type_bool,
            household("ny_clean_heat_residential_incentive", period),
            household("ny_clean_heat_multifamily_incentive", period),
        )
