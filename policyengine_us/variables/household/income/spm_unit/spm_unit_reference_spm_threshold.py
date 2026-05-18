import numpy as np

from policyengine_us.model_api import *
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)
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


class spm_unit_reference_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit reference SPM poverty threshold"
    documentation = "SPM reference threshold by tenure, before equivalence-scale and geographic adjustments."
    definition_period = YEAR
    unit = USD

    def formula_2015(spm_unit, period, parameters):
        cpi_u = parameters.gov.bls.cpi.cpi_u
        tenure = spm_unit("spm_unit_tenure_type", period)
        return _reference_threshold_array(
            tenure,
            period.start.year,
            cpi_u,
        )
