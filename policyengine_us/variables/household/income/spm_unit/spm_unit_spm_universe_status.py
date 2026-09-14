from policyengine_us.model_api import *
from policyengine_us.spm import default_spm_universe_status


class SPMUniverseStatus(Enum):
    INCLUDED = "Included in the declared SPM measurement universe"
    OUTSIDE = "Outside the declared SPM measurement universe"
    UNRESOLVED = "Measurement universe has not been resolved"


class spm_unit_spm_universe_status(Variable):
    value_type = Enum
    possible_values = SPMUniverseStatus
    default_value = SPMUniverseStatus.UNRESOLVED
    entity = SPMUnit
    definition_period = YEAR
    label = "SPM measurement universe status"
    reference = "https://www.census.gov/content/dam/Census/library/working-papers/2020/demo/SEHSD-WP2020-09.pdf#page=6"

    def formula(spm_unit, period, parameters):
        return default_spm_universe_status(spm_unit)
