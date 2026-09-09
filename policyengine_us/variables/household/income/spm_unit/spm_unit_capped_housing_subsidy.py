from policyengine_us.model_api import *
from spm_calculator.policyengine_adapter import policyengine_amount


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf"

    def formula(spm_unit, period, parameters):
        housing_assistance = spm_unit("housing_assistance", period).astype("float64")
        # Apply the country-owned cap to the unrounded canonical housing amount;
        # the model stores this final benefit amount with one dtype conversion.
        housing_portion = policyengine_amount(spm_unit, period, "housing_portion")
        tenant_payment = spm_unit("hud_ttp", period).astype("float64")
        cap = max_(housing_portion - tenant_payment, 0)
        return min_(housing_assistance, cap)
