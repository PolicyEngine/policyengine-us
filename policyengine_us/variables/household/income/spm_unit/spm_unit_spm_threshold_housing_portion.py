from policyengine_us.model_api import *
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)
from spm_calculator.geoadj import get_housing_share


SPM_TENURE_TYPE_TO_HOUSING_SHARE = {
    SPMUnitTenureType.OWNER_WITH_MORTGAGE: get_housing_share("owner_with_mortgage"),
    SPMUnitTenureType.OWNER_WITHOUT_MORTGAGE: get_housing_share(
        "owner_without_mortgage"
    ),
    SPMUnitTenureType.RENTER: get_housing_share("renter"),
}


def _housing_share_array(tenure):
    values = np.full(
        len(tenure),
        SPM_TENURE_TYPE_TO_HOUSING_SHARE[SPMUnitTenureType.RENTER],
        dtype=float,
    )
    for tenure_type, housing_share in SPM_TENURE_TYPE_TO_HOUSING_SHARE.items():
        values = np.where(tenure == tenure_type, housing_share, values)
    return values


class spm_unit_spm_threshold_housing_portion(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit SPM threshold housing portion"
    documentation = (
        "Geographically adjusted housing portion of the SPM poverty threshold."
    )
    definition_period = YEAR
    unit = USD

    def formula_2015(spm_unit, period, parameters):
        unadjusted_threshold = spm_unit(
            "spm_unit_unadjusted_spm_threshold",
            period,
        )
        geoadj = spm_unit("spm_unit_geographic_adjustment", period)
        tenure = spm_unit("spm_unit_tenure_type", period)
        housing_share = _housing_share_array(tenure)

        # The threshold applies geographic adjustment only to the housing
        # share: adjusted = unadjusted * (1 - h + h * local_rent_ratio).
        # Since geoadj = 1 - h + h * local_rent_ratio, the adjusted housing
        # share is h * local_rent_ratio = geoadj + h - 1.
        geoadjusted_housing_share = geoadj + housing_share - 1
        return unadjusted_threshold * geoadjusted_housing_share
