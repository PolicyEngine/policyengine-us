import numpy as np

from policyengine_us.model_api import *
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)
from spm_calculator.equivalence_scale import spm_equivalence_scale
from spm_calculator.forecast import (
    HISTORICAL_THRESHOLDS,
    get_latest_published_year,
)

LATEST_PUBLISHED_SPM_THRESHOLD_YEAR = get_latest_published_year()


def _reference_threshold_array(tenure, year: int, cpi_u_parameter):
    """Published Betson reference thresholds for ``year``, uprated past
    the latest BLS-published year using PolicyEngine's CPI-U parameter.

    The published values and three-tenure structure come from
    ``spm-calculator`` so there is one source of truth across the
    PolicyEngine stack.
    """
    if year <= LATEST_PUBLISHED_SPM_THRESHOLD_YEAR:
        thresholds = HISTORICAL_THRESHOLDS[year]
    else:
        factor = float(
            cpi_u_parameter(f"{year}-02-01")
            / cpi_u_parameter(f"{LATEST_PUBLISHED_SPM_THRESHOLD_YEAR}-02-01")
        )
        thresholds = {
            k: v * factor
            for k, v in HISTORICAL_THRESHOLDS[
                LATEST_PUBLISHED_SPM_THRESHOLD_YEAR
            ].items()
        }

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


class spm_unit_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's SPM poverty threshold"
    definition_period = YEAR
    unit = USD

    def formula_2015(spm_unit, period, parameters):
        """Rebuild the SPM threshold from current composition, current
        tenure, and the unit-specific geographic adjustment.

        Base reference thresholds and the Betson three-parameter
        equivalence scale come from ``spm-calculator``.
        """
        cpi_u = parameters.gov.bls.cpi.cpi_u

        current_adults = spm_unit("spm_unit_count_adults", period)
        current_children = spm_unit("spm_unit_count_children", period)
        current_tenure = spm_unit("spm_unit_tenure_type", period)
        geoadj = spm_unit("spm_unit_geographic_adjustment", period)
        current_base = _reference_threshold_array(
            current_tenure,
            period.start.year,
            cpi_u,
        )

        current_equiv_scale = spm_equivalence_scale(
            current_adults,
            current_children,
        )

        return current_base * current_equiv_scale * geoadj
