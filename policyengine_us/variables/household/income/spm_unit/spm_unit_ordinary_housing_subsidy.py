from policyengine_us.model_api import *
from policyengine_us.spm import spm_universe_mask
from spm_calculator.errors import SPMInputError


class spm_unit_ordinary_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Housing subsidy value in ordinary income aggregates"
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14"

    def formula(spm_unit, period, parameters):
        included = spm_universe_mask(spm_unit, period)
        assistance = spm_unit("housing_assistance", period).astype("float64")
        if not np.isfinite(assistance).all() or np.any(assistance < 0):
            raise SPMInputError(
                "SPM_HOUSING_ASSISTANCE_INVALID",
                "Ordinary housing assistance must be finite and nonnegative.",
            )
        outside_assisted = ~included & (assistance > 0)
        reported = spm_unit("spm_unit_ordinary_housing_subsidy_reported", period)
        values = reported[outside_assisted]
        if (
            not np.isfinite(values).all()
            or np.any(values < 0)
            or np.any(values > assistance[outside_assisted])
        ):
            raise SPMInputError(
                "SPM_ORDINARY_HOUSING_VALUE_REQUIRED",
                "Outside units with positive housing assistance require a "
                "source-supported ordinary housing value between zero and "
                "assistance, for the same unit and year. Retain its allocation "
                "and valuation provenance with the dataset; SPM scope alone "
                "does not establish that value.",
            )
        # Preserve the existing ordinary valuation for included units. Outside
        # values are explicitly supplied, never an invented SPM cap or uncap.
        capped = spm_unit("spm_unit_capped_housing_subsidy", period)
        return where(included, capped, where(outside_assisted, reported, 0))
