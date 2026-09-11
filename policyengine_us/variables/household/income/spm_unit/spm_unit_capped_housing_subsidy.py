from policyengine_us.model_api import *
from policyengine_us.spm import masked_policyengine_amount


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf"

    def formula(spm_unit, period, parameters):
        housing_assistance = spm_unit("housing_assistance", period).astype("float64")
        # Only a unit with housing assistance has anything to cap. Consulting
        # the canonical housing portion for the other units would demand SPM
        # geography and composition from resource and benefit consumers that
        # never use the measurement, so the cap is evaluated for assisted units
        # alone; every other unit's capped subsidy is zero by construction.
        assisted = housing_assistance > 0
        if not assisted.any():
            return np.zeros_like(housing_assistance)
        # Apply the country-owned cap to the unrounded canonical housing amount;
        # the model stores this final benefit amount with one dtype conversion.
        housing_portion = masked_policyengine_amount(
            spm_unit, period, "housing_portion", assisted
        )
        tenant_payment = spm_unit("hud_ttp", period).astype("float64")
        cap = max_(housing_portion - tenant_payment, 0)
        return where(assisted, min_(housing_assistance, cap), 0)
