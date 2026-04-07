from policyengine_us.model_api import *
from policyengine_us.tools.spm_thresholds import (
    get_spm_reference_thresholds,
    spm_equivalence_scale,
)
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)


class spm_unit_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's SPM poverty threshold"
    definition_period = YEAR
    unit = USD

    def formula_2024(spm_unit, period, parameters):
        prior_period = period.last_year
        cpi_u = parameters.gov.bls.cpi.cpi_u

        prior_threshold = spm_unit("spm_unit_spm_threshold", prior_period)
        prior_adults = spm_unit("spm_unit_count_adults", prior_period)
        prior_children = spm_unit("spm_unit_count_children", prior_period)
        prior_tenure = spm_unit("spm_unit_tenure_type", prior_period)

        current_adults = spm_unit("spm_unit_count_adults", period)
        current_children = spm_unit("spm_unit_count_children", period)
        current_tenure = spm_unit("spm_unit_tenure_type", period)

        prior_base = _reference_threshold_array(
            prior_tenure,
            prior_period.start.year,
            cpi_u,
        )
        current_base = _reference_threshold_array(
            current_tenure,
            period.start.year,
            cpi_u,
        )

        prior_equiv_scale = spm_equivalence_scale(prior_adults, prior_children)
        current_equiv_scale = spm_equivalence_scale(
            current_adults,
            current_children,
        )

        denominator = prior_base * prior_equiv_scale
        geoadj = np.divide(
            prior_threshold,
            denominator,
            out=np.ones_like(prior_threshold, dtype=float),
            where=denominator > 0,
        )
        return current_base * current_equiv_scale * geoadj


def _reference_threshold_array(tenure, year: int, cpi_u_parameter):
    thresholds = get_spm_reference_thresholds(year, cpi_u_parameter)
    values = np.full(len(tenure), thresholds["renter"], dtype=float)
    values = np.where(
        tenure == SPMUnitTenureType.OWNER_WITH_MORTGAGE,
        thresholds["owner_with_mortgage"],
        values,
    )
    values = np.where(
        tenure == SPMUnitTenureType.OWNER_WITHOUT_MORTGAGE,
        thresholds["owner_without_mortgage"],
        values,
    )
    return values
