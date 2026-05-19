from policyengine_us.model_api import *


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf"

    def formula(spm_unit, period, parameters):
        housing_assistance = spm_unit("housing_assistance", period)
        housing_portion = spm_unit(
            "spm_unit_spm_threshold_housing_portion",
            period,
        )
        tenant_payment = spm_unit("hud_ttp", period)
        cap = max_(housing_portion - tenant_payment, 0)
        return min_(housing_assistance, cap)
