from policyengine_us.model_api import *
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)
from spm_calculator.geoadj import get_cd_geoadj


SPM_TENURE_TYPE_TO_GEOADJ_KEY = {
    SPMUnitTenureType.OWNER_WITH_MORTGAGE: "owner_with_mortgage",
    SPMUnitTenureType.OWNER_WITHOUT_MORTGAGE: "owner_without_mortgage",
    SPMUnitTenureType.RENTER: "renter",
}


def _cd_geoadj_array(cd_geoids, tenure, geoadj_year: int = 2023):
    geoadj = np.ones(len(cd_geoids), dtype=float)
    valid_cd = cd_geoids > 0

    for tenure_enum, tenure_key in SPM_TENURE_TYPE_TO_GEOADJ_KEY.items():
        tenure_mask = valid_cd & (tenure == tenure_enum)
        for cd_geoid in np.unique(cd_geoids[tenure_mask]):
            try:
                value = get_cd_geoadj(
                    int(cd_geoid),
                    year=geoadj_year,
                    tenure=tenure_key,
                )
            except ValueError:
                value = 1.0
            geoadj[tenure_mask & (cd_geoids == cd_geoid)] = value

    return geoadj


class spm_unit_geographic_adjustment(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit geographic adjustment"
    documentation = "Geographic adjustment applied to the SPM reference threshold."
    definition_period = YEAR
    default_value = 1.0

    def formula_2015(spm_unit, period, parameters):
        cd_geoids = spm_unit.household("congressional_district_geoid", period)
        tenure = spm_unit("spm_unit_tenure_type", period)
        return _cd_geoadj_array(cd_geoids, tenure)
