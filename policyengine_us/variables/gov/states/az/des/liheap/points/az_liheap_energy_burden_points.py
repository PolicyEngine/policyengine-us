from policyengine_us.model_api import *


class az_liheap_energy_burden_points(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP energy burden points"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap

        # Get energy costs
        energy_costs = add(
            spm_unit,
            period,
            ["heating_cooling_expense", "electricity_expense", "gas_expense"],
        )

        # Get household income (use gross income for LIHEAP)
        income = spm_unit("az_liheap_countable_income", period)

        # Calculate energy burden as percentage of income
        # Avoid division by zero
        energy_burden = where(income > 0, energy_costs / income, 0)

        # Determine points based on energy burden
        thresholds = p.energy_burden_thresholds
        points_table = p.points.energy_burden

        return select(
            [
                energy_burden < thresholds.threshold_1,  # <1%
                energy_burden < thresholds.threshold_2,  # 1-2%
                energy_burden < thresholds.threshold_4,  # 3-5%
                energy_burden < thresholds.threshold_6,  # 6-10%
                energy_burden < thresholds.threshold_8,  # 11-15%
                energy_burden <= thresholds.threshold_10,  # 16-20%
                energy_burden > thresholds.threshold_10,  # >20%
            ],
            [
                points_table.below_1,
                points_table["1_to_2"],
                points_table["3_to_5"],
                points_table["6_to_10"],
                points_table["11_to_15"],
                points_table["16_to_20"],
                points_table.above_20,
            ],
            default=points_table.below_1,
        )
