from policyengine_us.model_api import *


class az_liheap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP base benefit"
    definition_period = YEAR
    defined_for = "az_liheap_eligible"
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap

        # Get total points
        total_points = spm_unit("az_liheap_total_points", period)

        # Determine benefit based on points
        thresholds = p.points_thresholds
        benefit_matrix = p.benefit_matrix

        return select(
            [
                total_points < thresholds.level_1,  # 0-3 points
                total_points < thresholds.level_2,  # 4-5 points
                total_points < thresholds.level_3,  # 6-7 points
                total_points < thresholds.level_4,  # 8-9 points
                total_points < thresholds.level_5,  # 10-11 points
                total_points < thresholds.level_6,  # 12-13 points
                total_points < thresholds.level_7,  # 14-15 points
                total_points >= thresholds.level_7,  # 16+ points
            ],
            [
                benefit_matrix["0_to_3"],
                benefit_matrix["4_to_5"],
                benefit_matrix["6_to_7"],
                benefit_matrix["8_to_9"],
                benefit_matrix["10_to_11"],
                benefit_matrix["12_to_13"],
                benefit_matrix["14_to_15"],
                benefit_matrix["16_plus"],
            ],
            default=benefit_matrix["0_to_3"],
        )
