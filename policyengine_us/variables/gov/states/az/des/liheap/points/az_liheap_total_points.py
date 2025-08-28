from policyengine_us.model_api import *


class az_liheap_total_points(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP total points"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        # Sum all points from different categories
        income_points = spm_unit("az_liheap_income_level_points", period)
        energy_burden_points = spm_unit(
            "az_liheap_energy_burden_points", period
        )
        vulnerable_points = spm_unit(
            "az_liheap_vulnerable_household_points", period
        )

        return income_points + energy_burden_points + vulnerable_points
