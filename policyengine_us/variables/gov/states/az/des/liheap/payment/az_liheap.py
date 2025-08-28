from policyengine_us.model_api import *


class az_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP payment"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = (
        "https://des.az.gov/services/basic-needs/liheap",
        "45 CFR Part 96 Subpart H",
    )

    def formula(spm_unit, period, parameters):
        # Get base benefit and crisis assistance
        base_benefit = spm_unit("az_liheap_base_benefit", period)
        crisis_assistance = spm_unit("az_liheap_crisis_assistance", period)

        # Total payment is base benefit plus any crisis assistance
        total_benefit = base_benefit + crisis_assistance

        # Limit benefit to actual energy costs
        actual_energy_costs = add(
            spm_unit,
            period,
            ["heating_cooling_expense", "electricity_expense", "gas_expense"],
        )

        return min_(total_benefit, actual_energy_costs)
