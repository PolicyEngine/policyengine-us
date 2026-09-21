from policyengine_us.model_api import *
from policyengine_us.spm import masked_policyengine_amount, spm_universe_mask
from spm_calculator.errors import SPMInputError


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf"

    def formula(spm_unit, period, parameters):
        included = spm_universe_mask(spm_unit, period)
        housing_assistance = spm_unit(
            "spm_unit_allocated_housing_subsidy", period
        ).astype("float64")
        if not np.isfinite(housing_assistance[included]).all() or np.any(
            housing_assistance[included] < 0
        ):
            raise SPMInputError(
                "SPM_HOUSING_ASSISTANCE_INVALID",
                "Included allocated housing assistance must be finite and nonnegative.",
            )
        # Only a unit allocated housing assistance has anything to cap. Consulting
        # the canonical housing portion for the other units would demand SPM
        # geography and composition from resource and benefit consumers that
        # never use the measurement, so the cap is evaluated for assisted units
        # alone. Other included units receive zero; outside units remain missing.
        assisted = included & (housing_assistance > 0)
        if not assisted.any():
            return np.where(included, 0, np.nan)
        # Apply the country-owned cap to the unrounded canonical housing amount;
        # the model stores this final benefit amount with one dtype conversion.
        housing_portion = masked_policyengine_amount(
            spm_unit, period, "housing_portion", assisted
        )
        tenant_payment = spm_unit("spm_unit_allocated_tenant_payment", period).astype(
            "float64"
        )
        cap = max_(housing_portion - tenant_payment, 0)
        return where(
            included, where(assisted, min_(housing_assistance, cap), 0), np.nan
        )
