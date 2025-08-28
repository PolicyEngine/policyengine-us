from policyengine_us.model_api import *


class az_liheap_income_level_points(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP income level points"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap

        # Get household income and poverty level
        income = spm_unit("az_liheap_countable_income", period)
        poverty_guideline = spm_unit("spm_unit_fpg", period)

        # Calculate income as percentage of poverty
        poverty_ratio = income / poverty_guideline

        # Determine points based on poverty level
        thresholds = p.income_poverty_thresholds
        points_table = p.points.income_level

        return select(
            [
                poverty_ratio <= thresholds.threshold_1,  # 0-30%
                poverty_ratio <= thresholds.threshold_2,  # 31-50%
                poverty_ratio <= thresholds.threshold_3,  # 51-75%
                poverty_ratio <= thresholds.threshold_4,  # 76-100%
                poverty_ratio <= thresholds.threshold_5,  # 101-125%
                poverty_ratio <= thresholds.threshold_6,  # 126-150%
            ],
            [
                points_table["0_to_30"],
                points_table["31_to_50"],
                points_table["51_to_75"],
                points_table["76_to_100"],
                points_table["101_to_125"],
                points_table["126_to_150"],
            ],
            default=points_table["126_to_150"],  # Above 150% gets 0 points
        )
